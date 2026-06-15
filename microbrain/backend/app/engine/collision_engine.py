from app.engine.kb import has_any


def detect_collision(narrative_before: dict, narrative_model: dict, mental_model: dict, intent: dict) -> dict:
    text = " ".join(
        str(value or "")
        for value in [
            narrative_model.get("stated_goal"),
            narrative_model.get("stated_problem"),
            " ".join(narrative_model.get("stated_constraints") or []),
            " ".join(narrative_model.get("stated_beliefs") or []),
        ]
    )
    evidence = []
    collision_type = "none"
    severity = 0.0

    if has_any(text, ["mas tabs", "mas debug", "ver todo", "demasiada informacion"]):
        collision_type = "scope_explosion"
        severity = 0.86
        evidence.append("diagnostics are leaking into user surface")
    elif has_any(text, ["no es sandbox", "reconstruible", "sin perder contrato"]):
        collision_type = "contract_violation"
        severity = 0.84
        evidence.append("user expects reconstructable contract")
    elif intent.get("explicit") == "move to implementation" and "contract" not in mental_model.get("salience", []):
        collision_type = "implementation_without_design"
        severity = 0.76
        evidence.append("implementation requested without contract salience")
    elif has_any(text, ["no validamos", "sin metricas"]) or (
        intent.get("explicit") in ["build system", "move to implementation"] and "validation_required" in narrative_model.get("validations", [])
    ):
        collision_type = "design_without_validation"
        severity = 0.8
        evidence.append("build/design is moving without validation evidence")
    elif narrative_before.get("objective") and narrative_model.get("objective") and narrative_before.get("objective") != narrative_model.get("objective") and has_any(text, ["original", "no un chatbot", "objetivo cambio"]):
        collision_type = "goal_drift"
        severity = 0.78
        evidence.append("new goal conflicts with stored objective")
    elif has_any(text, ["dependencias ocultas"]):
        collision_type = "hidden_dependency"
        severity = 0.7
        evidence.append("dependency mentioned without explicit architecture path")
    elif has_any(text, ["sobreinfiera"]):
        collision_type = "over_inference"
        severity = 0.68
        evidence.append("user flags inference boundary risk")
    elif not narrative_model.get("objective") and not narrative_before.get("objective"):
        collision_type = "missing_context"
        severity = 0.42
        evidence.append("objective is not explicit yet")

    return {"exists": collision_type != "none", "type": collision_type, "severity": severity, "evidence": evidence}
