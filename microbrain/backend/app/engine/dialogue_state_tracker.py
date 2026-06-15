from copy import deepcopy


def update_narrative_with_dialogue_state(
    narrative_after: dict,
    narrative_before: dict,
    gap_resolution: dict,
    anticipation: dict,
    domain_state: dict,
) -> dict:
    updated = deepcopy(narrative_after)
    resolved = set(domain_state.get("resolved_gaps") or [])
    previous_loops = [loop for loop in narrative_before.get("open_loops") or [] if loop not in resolved]
    next_gap = gap_resolution.get("blocking_gap") or infer_next_gap(updated, domain_state, resolved)

    if gap_resolution.get("input_contract"):
        updated["input_contract"] = gap_resolution["input_contract"]
    elif narrative_before.get("input_contract"):
        updated["input_contract"] = narrative_before["input_contract"]

    if gap_resolution.get("output_contract"):
        updated["output_contract"] = gap_resolution["output_contract"]
    elif narrative_before.get("output_contract"):
        updated["output_contract"] = narrative_before["output_contract"]

    updated["resolved_gaps"] = list(resolved)
    updated["active_domain"] = domain_state.get("active_domain")
    updated["domain_state"] = domain_state
    updated["anticipation_gaps"] = anticipation.get("anticipation_gaps", [])
    updated["inferred_data"] = anticipation.get("inferred_data", [])

    if next_gap:
        updated["blocking_gap"] = next_gap
        updated["open_loops"] = ordered_unique([next_gap] + previous_loops)
    else:
        updated["open_loops"] = previous_loops
        if updated.get("blocking_gap") in resolved:
            updated["blocking_gap"] = previous_loops[0] if previous_loops else None

    if updated.get("object_graph"):
        gaps = []
        if updated.get("blocking_gap"):
            gaps.append({"type": updated["blocking_gap"], "blocking": True})
        updated["object_graph"] = {**updated["object_graph"], "gaps": gaps}

    return updated


def ordered_unique(items: list[str]) -> list[str]:
    result = []
    for item in items:
        if item and item not in result:
            result.append(item)
    return result


def infer_next_gap(narrative: dict, domain_state: dict, resolved: set[str]) -> str | None:
    central_objects = narrative.get("central_objects") or []
    prompt_like = any(item in central_objects for item in ["prompt_generator", "render_prompt_generator"])
    active_domain = domain_state.get("active_domain") or narrative.get("active_domain")
    if prompt_like and not narrative.get("input_contract") and "missing_io_contract" not in resolved:
        return "missing_io_contract"
    if narrative.get("input_contract") and not narrative.get("output_contract") and "missing_output_contract" not in resolved:
        return "missing_output_contract"
    if active_domain == "midjourney_v8_1_core" and narrative.get("output_contract") and "missing_domain_parameters" not in resolved:
        return "missing_domain_parameters"
    return None
