from app.engine.kb import MOVES


def build_response_plan(intent: dict, collision: dict, implications: dict) -> dict:
    move = "align"
    if collision["type"] == "scope_explosion":
        move = "warn"
    elif collision["type"] == "contract_violation":
        move = "correct"
    elif collision["type"] == "implementation_without_design":
        move = "freeze_contract"
    elif collision["type"] == "design_without_validation":
        move = "test"
    elif collision["type"] == "goal_drift":
        move = "align"
    elif intent.get("explicit") == "choose next move":
        move = "propose_next_step"
    elif intent.get("explicit") == "validate engine":
        move = "test"
    elif intent.get("explicit") == "audit system":
        move = "warn"

    if move not in MOVES:
        move = "align"

    return {
        "move": move,
        "purpose": f"{move} system narrative before further build",
        "must_include": ["collision status", "narrative current state", "next architectural move"],
        "must_avoid": ["raw debug dump", "generic encouragement", "therapy language", "clinical labels"],
    }
