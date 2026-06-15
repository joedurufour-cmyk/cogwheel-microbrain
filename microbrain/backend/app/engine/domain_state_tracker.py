import json

from sqlalchemy.orm import Session as DbSession

from app import models


def empty_domain_state() -> dict:
    return {
        "active_domain": "system_design_navigation",
        "domain_parameters": {},
        "resolved_gaps": [],
        "anticipation_gaps": [],
        "next_action_prompt": "",
        "domain_confidence": 0,
    }


def load_domain_state(db: DbSession, session_id: int) -> dict:
    state = db.query(models.DomainState).filter(models.DomainState.session_id == session_id).one_or_none()
    if not state:
        return empty_domain_state()
    return {
        "active_domain": state.active_domain,
        "domain_parameters": json.loads(state.domain_parameters_json or "{}"),
        "resolved_gaps": json.loads(state.resolved_gaps_json or "[]"),
        "anticipation_gaps": json.loads(state.anticipation_gaps_json or "[]"),
        "next_action_prompt": state.next_action_prompt or "",
        "domain_confidence": state.domain_confidence,
    }


def update_domain_state(
    domain_state_before: dict,
    active_domain: str,
    gap_resolution: dict,
    extracted_objects: dict,
    domain_contract,
) -> dict:
    resolved = ordered_unique((domain_state_before.get("resolved_gaps") or []) + gap_resolution.get("resolved_gaps", []))
    parameters = {
        **(domain_state_before.get("domain_parameters") or {}),
        **(gap_resolution.get("domain_parameters") or {}),
    }
    confidence = 0.9 if active_domain == "midjourney_v8_1_core" else max(domain_state_before.get("domain_confidence") or 0, 0.4)

    return {
        "active_domain": active_domain,
        "domain_parameters": parameters,
        "resolved_gaps": resolved,
        "anticipation_gaps": domain_state_before.get("anticipation_gaps") or [],
        "next_action_prompt": next_action_prompt(gap_resolution),
        "domain_confidence": confidence,
    }


def detect_anticipation_gaps(domain_state: dict, domain_contract, inferred_data: list[str] | None = None) -> dict:
    inferred_data = inferred_data or []
    gaps = list(domain_state.get("anticipation_gaps") or [])
    parameters = domain_state.get("domain_parameters") or {}

    if domain_contract.domain_id == "midjourney_v8_1_core":
        if "cinematic_candidate_aspect_ratio" in inferred_data and not parameters.get("aspect_ratio"):
            gaps.append("confirm_aspect_ratio")
        if not parameters.get("stylize"):
            gaps.append("confirm_stylization_level")

    return {"anticipation_gaps": ordered_unique(gaps), "inferred_data": inferred_data}


def persist_domain_state(db: DbSession, session_id: int, domain_state: dict) -> None:
    state = db.query(models.DomainState).filter(models.DomainState.session_id == session_id).one_or_none()
    if not state:
        state = models.DomainState(session_id=session_id)
        db.add(state)
    state.active_domain = domain_state.get("active_domain") or "system_design_navigation"
    state.domain_parameters_json = json.dumps(domain_state.get("domain_parameters") or {})
    state.resolved_gaps_json = json.dumps(domain_state.get("resolved_gaps") or [])
    state.anticipation_gaps_json = json.dumps(domain_state.get("anticipation_gaps") or [])
    state.next_action_prompt = domain_state.get("next_action_prompt") or ""
    state.domain_confidence = domain_state.get("domain_confidence") or 0


def next_action_prompt(gap_resolution: dict) -> str:
    if gap_resolution.get("blocking_gap") == "missing_output_contract":
        return "definir contrato de salida"
    if gap_resolution.get("blocking_gap") == "missing_domain_parameters":
        return "confirmar parametros de dominio"
    if gap_resolution.get("resolved_gaps"):
        return "continuar al siguiente bloqueo"
    return ""


def ordered_unique(items: list[str]) -> list[str]:
    result = []
    for item in items:
        if item and item not in result:
            result.append(item)
    return result

