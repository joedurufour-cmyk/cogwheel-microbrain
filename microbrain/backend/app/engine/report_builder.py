def build_report(
    raw_input: str,
    narrative_before: dict,
    narrative_after: dict,
    segments: list[dict],
    mental_model: dict,
    intent: dict,
    collision: dict,
    implications: dict,
    response_plan: dict,
    answer: str,
) -> dict:
    return {
        "what_i_detected": [
            f"segments={len(segments)}",
            f"intent={intent.get('explicit') or intent.get('latent')}",
            f"collision={collision.get('type')}",
            f"load={mental_model.get('load')}",
        ],
        "what_i_updated_in_memory": memory_changes(narrative_before, narrative_after),
        "narrative_before": narrative_before,
        "narrative_after": narrative_after,
        "collisions_found": [collision] if collision.get("exists") else [],
        "implication_used": implications.get("implications", []),
        "response_plan": response_plan,
        "answer_given": answer,
    }


def memory_changes(before: dict, after: dict) -> list[str]:
    changes = []
    for key in ["objective", "active_problem", "current_hypothesis"]:
        if before.get(key) != after.get(key):
            changes.append(f"{key}: {before.get(key)} -> {after.get(key)}")
    for key in ["current_architecture", "current_risks", "open_loops", "validations"]:
        if before.get(key) != after.get(key):
            changes.append(f"{key} updated")
    return changes
