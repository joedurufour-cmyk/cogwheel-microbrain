def infer_implications(narrative_model: dict, collision: dict, intent: dict) -> dict:
    implications = []
    risks = []
    next_best_move = next_move_from_state(narrative_model) or "define system objective"

    if collision["type"] == "scope_explosion":
        implications.append("diagnostics may overwhelm normal users")
        risks.append("debug surface becomes product surface")
        next_best_move = "hide diagnostics behind developer mode"
    elif collision["type"] == "contract_violation":
        implications.append("system may not be reconstructable")
        risks.append("contract cannot be audited reliably")
        next_best_move = "switch to reconstructable system contract"
    elif collision["type"] == "implementation_without_design":
        implications.append("implementation may proceed without frozen architecture")
        risks.append("code churn without narrative stability")
        next_best_move = "freeze contract before coding"
    elif collision["type"] == "design_without_validation":
        implications.append("validation missing")
        implications.append("build may continue without evidence")
        risks.append("features accumulate without proof")
        next_best_move = "define test cases before adding features"
    elif collision["type"] == "goal_drift":
        implications.append("original narrative may be lost")
        risks.append("system becomes generic chatbot")
        next_best_move = "realign objective and active problem"
    elif collision["type"] == "over_inference":
        implications.append("engine needs stricter evidence threshold")
        risks.append("answer may exceed user-provided facts")
        next_best_move = "add over-inference guard to response planner"
    elif intent.get("explicit") == "choose next move":
        implications.append("user needs an architectural action, not explanation")
        next_best_move = "choose one next architectural move"

    inferred_risk = narrative_model.get("current_risks", [None])[-1] if narrative_model.get("current_risks") else None
    if inferred_risk and inferred_risk not in risks:
        risks.append(inferred_risk)

    return {"implications": implications, "risks": risks, "next_best_move": next_best_move}


def next_move_from_state(narrative_model: dict) -> str | None:
    blocking_gap = narrative_model.get("blocking_gap")
    by_gap = next_move_from_gap(blocking_gap)
    if by_gap:
        return by_gap
    resolved = set(narrative_model.get("resolved_gaps") or [])
    active_domain = narrative_model.get("active_domain")
    if narrative_model.get("phase") == "EXECUTION":
        return "COMPILE_DOMAIN_PROMPT"
    if active_domain == "midjourney_v8_1_core" and "missing_domain_parameters" in resolved:
        return "COMPILE_DOMAIN_PROMPT"
    if narrative_model.get("input_contract") and narrative_model.get("output_contract"):
        return "generar salida con el contrato definido"
    return None


def next_move_from_gap(blocking_gap: str | None) -> str | None:
    if blocking_gap == "missing_io_contract":
        return "definir contrato de entrada"
    if blocking_gap == "missing_output_contract":
        return "definir contrato de salida"
    if blocking_gap == "missing_domain_parameters":
        return "confirmar parametros de dominio"
    return None
