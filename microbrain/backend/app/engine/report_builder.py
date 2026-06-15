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
    object_extraction: dict | None = None,
    relationship_graph: dict | None = None,
    gap_resolution: dict | None = None,
    domain_state: dict | None = None,
    active_domain_contract: dict | None = None,
    anticipation: dict | None = None,
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
        "object_extraction": object_extraction or {},
        "relationship_graph": relationship_graph or {},
        "gap_resolution": gap_resolution or {},
        "domain_state": domain_state or {},
        "active_domain_contract": active_domain_contract or {},
        "anticipation_gaps": (anticipation or {}).get("anticipation_gaps", []),
        "response_plan": response_plan,
        "answer_given": answer,
    }


def memory_changes(before: dict, after: dict) -> list[str]:
    changes = []
    for key in ["objective", "active_problem", "current_hypothesis"]:
        if before.get(key) != after.get(key):
            changes.append(f"{key}: {before.get(key)} -> {after.get(key)}")
    for key in ["current_architecture", "current_risks", "open_loops", "validations", "resolved_gaps"]:
        if before.get(key) != after.get(key):
            changes.append(f"{key} updated")
    return changes
