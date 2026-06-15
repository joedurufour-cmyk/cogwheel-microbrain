import os
from typing import Any

import httpx
from pydantic import ValidationError

from app.engine.domain_schema_registry import inject_domain_schema


def domain_compiler_node(narrative_state: dict, domain_state: dict, domain_contract) -> dict:
    next_move = domain_state.get("next_action_prompt") or ""
    if next_move == "REQUIRE_WEB_SEARCH":
        web_context = execute_web_search_stub(domain_state.get("domain_parameters", {}))
        domain_state = {
            **domain_state,
            "domain_parameters": {**(domain_state.get("domain_parameters") or {}), "web_context": web_context},
        }

    if next_move != "EXECUTE_DOMAIN_COMPILER" and narrative_state.get("phase") != "EXECUTION":
        return {"status": "idle", "output_envelope": None, "final_compiled_system": None, "validation_errors": []}

    parameters = domain_state.get("domain_parameters") or {}
    DynamicSchema = inject_domain_schema(domain_state.get("active_domain") or "generic", parameters)
    payload = normalize_payload_for_schema(DynamicSchema, parameters, narrative_state)

    try:
        validated_data = DynamicSchema(**payload)
    except ValidationError as error:
        return {
            "status": "validation_failed",
            "output_envelope": build_output_envelope(
                domain_state.get("active_domain") or "generic",
                narrative_state,
                domain_state,
                domain_contract,
                validated_data=None,
                deliverables=[],
                validation_errors=error.errors(),
            ),
            "final_compiled_system": None,
            "validation_errors": error.errors(),
        }

    deliverables = compile_domain_deliverables(
        domain_state.get("active_domain") or "generic",
        validated_data.model_dump(),
        narrative_state,
        domain_contract,
    )
    output_envelope = build_output_envelope(
        domain_state.get("active_domain") or "generic",
        narrative_state,
        domain_state,
        domain_contract,
        validated_data=validated_data.model_dump(),
        deliverables=deliverables,
        validation_errors=[],
    )
    return {
        "status": "compiled",
        "schema_name": DynamicSchema.__name__,
        "validated_data": validated_data.model_dump(),
        "output_envelope": output_envelope,
        "final_compiled_system": output_envelope,
        "validation_errors": [],
    }


def normalize_payload_for_schema(schema, parameters: dict[str, Any], narrative_state: dict) -> dict:
    payload = {}
    for field_name in schema.model_fields:
        if field_name in parameters:
            payload[field_name] = parameters[field_name]
        elif field_name == "version":
            payload[field_name] = parameters.get("version") or "8.1"
        elif field_name == "base_prompt":
            payload[field_name] = extract_base_prompt(narrative_state)
        elif field_name == "raw_parameters":
            payload[field_name] = parameters
    return payload


def compile_domain_deliverables(domain_id: str, validated_data: dict, narrative_state: dict, domain_contract) -> list[dict]:
    if domain_id == "midjourney_v8_1_core":
        base_prompt = extract_base_prompt(narrative_state)
        parameters = [
            f"--ar {validated_data['aspect_ratio']}",
            f"--s {validated_data['stylize']}",
            f"--v {validated_data.get('version') or '8.1'}",
        ]
        domain_parameters = narrative_state.get("domain_state", {}).get("domain_parameters", {})
        if "chaos" in domain_parameters:
            parameters.append(f"--chaos {domain_parameters['chaos']}")
        if "seed" in domain_parameters:
            parameters.append(f"--seed {domain_parameters['seed']}")
        return [
            {
                "artifact_type": "prompt_package",
                "positive_prompt": base_prompt,
                "negative_prompt": "optional",
                "parameters": " ".join(parameters),
                "compiled_preview": f"{base_prompt} {' '.join(parameters)}".strip(),
            }
        ]

    return [
        {
            "artifact_type": infer_artifact_type(narrative_state, domain_contract),
            "validated_data": validated_data,
            "output_schema": getattr(domain_contract, "output_schema", {}),
        }
    ]


def build_output_envelope(
    domain_id: str,
    narrative_state: dict,
    domain_state: dict,
    domain_contract,
    validated_data: dict | None,
    deliverables: list[dict],
    validation_errors: list,
) -> dict:
    return {
        "artifact_type": infer_artifact_type(narrative_state, domain_contract),
        "domain_id": domain_id,
        "phase": narrative_state.get("phase"),
        "objective": narrative_state.get("objective"),
        "central_object": (narrative_state.get("central_objects") or [None])[0],
        "io_contract": {
            "input": narrative_state.get("input_contract") or {},
            "output": narrative_state.get("output_contract") or {},
        },
        "domain_parameters": domain_state.get("domain_parameters") or {},
        "validation": {
            "status": "failed" if validation_errors else "passed",
            "schema": f"{domain_id}_Schema",
            "validated_data": validated_data,
            "errors": validation_errors,
        },
        "deliverables": deliverables,
        "next_runtime_action": "EXECUTE_OUTPUT_RENDERER" if not validation_errors else "REPAIR_DOMAIN_CONTRACT",
    }


def infer_artifact_type(narrative_state: dict, domain_contract) -> str:
    output_contract = narrative_state.get("output_contract") or {}
    includes = output_contract.get("includes") or []
    if any(item in includes for item in ["positive_prompt", "negative_prompt", "technical_parameters"]):
        return "prompt_package"
    if any(item in includes for item in ["micro_app", "app_spec", "ui_spec"]):
        return "micro_app_spec"
    if any(item in includes for item in ["legal_contract", "clause_summary"]):
        return "document_package"
    output_schema = getattr(domain_contract, "output_schema", {}) or {}
    if output_schema:
        return output_schema.get("artifact_type") or "domain_artifact"
    return "domain_artifact"


def extract_base_prompt(narrative_state: dict) -> str:
    objective = narrative_state.get("objective") or ""
    central = (narrative_state.get("central_objects") or ["system"])[0]
    return f"{objective} / {central}".strip(" /")


def execute_web_search_stub(parameters: dict) -> dict:
    api_key = os.getenv("TAVILY_API_KEY")
    query = " ".join(str(value) for value in parameters.values() if value is not None).strip()
    if api_key and query:
        try:
            response = httpx.post(
                "https://api.tavily.com/search",
                json={"api_key": api_key, "query": query, "search_depth": "basic", "max_results": 3},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            return {
                "status": "ok",
                "results": [
                    {
                        "title": item.get("title"),
                        "url": item.get("url"),
                        "content": item.get("content"),
                    }
                    for item in data.get("results", [])
                ],
            }
        except Exception as error:
            return {"status": "error", "reason": str(error), "parameters_seen": sorted(parameters.keys())}
    return {
        "status": "not_configured",
        "reason": "web search hook available; no production provider configured",
        "parameters_seen": sorted(parameters.keys()),
    }
