from typing import Any

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
        return {"status": "idle", "final_compiled_system": None, "validation_errors": []}

    parameters = domain_state.get("domain_parameters") or {}
    DynamicSchema = inject_domain_schema(domain_state.get("active_domain") or "generic", parameters)
    payload = normalize_payload_for_schema(DynamicSchema, parameters, narrative_state)

    try:
        validated_data = DynamicSchema(**payload)
    except ValidationError as error:
        return {
            "status": "validation_failed",
            "final_compiled_system": None,
            "validation_errors": error.errors(),
        }

    final_output = compile_domain_output(
        domain_state.get("active_domain") or "generic",
        validated_data.model_dump(),
        narrative_state,
        domain_contract,
    )
    return {
        "status": "compiled",
        "schema_name": DynamicSchema.__name__,
        "validated_data": validated_data.model_dump(),
        "final_compiled_system": final_output,
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


def compile_domain_output(domain_id: str, validated_data: dict, narrative_state: dict, domain_contract) -> dict:
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
        return {
            "type": "midjourney_prompt_contract",
            "positive_prompt": base_prompt,
            "negative_prompt": "optional",
            "parameters": " ".join(parameters),
            "compiled": f"{base_prompt} {' '.join(parameters)}".strip(),
        }

    return {
        "type": "generic_domain_contract",
        "domain_id": domain_id,
        "validated_data": validated_data,
        "output_schema": getattr(domain_contract, "output_schema", {}),
    }


def extract_base_prompt(narrative_state: dict) -> str:
    objective = narrative_state.get("objective") or ""
    central = (narrative_state.get("central_objects") or ["system"])[0]
    return f"{objective} / {central}".strip(" /")


def execute_web_search_stub(parameters: dict) -> dict:
    return {
        "status": "not_configured",
        "reason": "web search hook available; no production provider configured",
        "parameters_seen": sorted(parameters.keys()),
    }

