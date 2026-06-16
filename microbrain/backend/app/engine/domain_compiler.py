import os

import httpx

from app.engine.output_compilers import (
    compile_advanced_prompt,
    compile_app_stack,
    compile_csv,
    compile_python_code,
    compile_text,
    detect_output_type,
)


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

    output_type = detect_output_type(narrative_state, domain_state)
    deliverable = _dispatch_compiler(output_type, narrative_state, domain_state, domain_contract)
    output_envelope = _build_output_envelope(
        domain_id=domain_state.get("active_domain") or "generic",
        narrative_state=narrative_state,
        domain_state=domain_state,
        output_type=output_type,
        deliverables=[deliverable],
    )
    return {
        "status": "compiled",
        "output_type": output_type,
        "output_envelope": output_envelope,
        "final_compiled_system": output_envelope,
        "validation_errors": [],
    }


def _dispatch_compiler(output_type: str, narrative_state: dict, domain_state: dict, domain_contract) -> dict:
    if output_type == "app_stack":
        return compile_app_stack(narrative_state, domain_state)
    if output_type == "python_code":
        return compile_python_code(narrative_state, domain_state)
    if output_type == "csv":
        return compile_csv(narrative_state, domain_state)
    if output_type == "advanced_prompt":
        return compile_advanced_prompt(narrative_state, domain_state)
    return compile_text(narrative_state, domain_state)


def _build_output_envelope(
    domain_id: str,
    narrative_state: dict,
    domain_state: dict,
    output_type: str,
    deliverables: list[dict],
) -> dict:
    return {
        "output_type": output_type,
        "domain_id": domain_id,
        "phase": narrative_state.get("phase"),
        "objective": narrative_state.get("objective"),
        "central_object": (narrative_state.get("central_objects") or [None])[0],
        "io_contract": {
            "input": narrative_state.get("input_contract") or {},
            "output": narrative_state.get("output_contract") or {},
        },
        "domain_parameters": domain_state.get("domain_parameters") or {},
        "deliverables": deliverables,
        "next_runtime_action": "EXECUTE_OUTPUT_RENDERER",
    }


def execute_web_search_stub(parameters: dict) -> dict:
    api_key = os.getenv("TAVILY_API_KEY")
    query = " ".join(str(v) for v in parameters.values() if v is not None).strip()
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
                    {"title": item.get("title"), "url": item.get("url"), "content": item.get("content")}
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
