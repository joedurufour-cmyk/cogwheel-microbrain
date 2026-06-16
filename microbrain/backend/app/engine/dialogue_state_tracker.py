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

    # Midjourney: if gap_resolution set missing_domain_parameters as next, redirect to scene first
    if (
        next_gap == "missing_domain_parameters"
        and domain_state.get("active_domain") == "midjourney_v8_1_core"
        and not (domain_state.get("domain_parameters") or {}).get("scene_description")
        and "missing_scene_description" not in resolved
    ):
        next_gap = "missing_scene_description"

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
    phase = infer_phase(updated, domain_state, resolved)
    updated["phase"] = phase
    if phase == "EXECUTION":
        updated["active_problem"] = None

    if next_gap:
        updated["blocking_gap"] = next_gap
        updated["open_loops"] = ordered_unique([next_gap] + previous_loops)
    else:
        updated["open_loops"] = previous_loops
        if updated.get("blocking_gap") in resolved:
            updated["blocking_gap"] = previous_loops[0] if previous_loops else None
        # Midjourney: clear stale domain_parameters blocking gap when scene was just resolved
        elif (
            "missing_scene_description" in (gap_resolution.get("resolved_gaps") or [])
            and updated.get("blocking_gap") == "missing_domain_parameters"
        ):
            updated["blocking_gap"] = None

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
    # Midjourney: scene description is the compilation prerequisite
    if active_domain == "midjourney_v8_1_core" and narrative.get("output_contract"):
        has_scene = bool((domain_state.get("domain_parameters") or {}).get("scene_description"))
        if not has_scene and "missing_scene_description" not in resolved:
            return "missing_scene_description"
        return None  # Scene captured → ready to compile
    if active_domain and active_domain != "system_design_navigation" and narrative.get("output_contract") and "missing_domain_parameters" not in resolved:
        return "missing_domain_parameters"
    return None


def infer_phase(narrative: dict, domain_state: dict, resolved: set[str]) -> str:
    central_objects = narrative.get("central_objects") or []
    has_scope = bool(narrative.get("objective") and central_objects)
    has_contract = bool(narrative.get("input_contract") and narrative.get("output_contract"))
    active_domain = domain_state.get("active_domain") or narrative.get("active_domain")
    # Midjourney reaches EXECUTION once scene is captured (tech flags optional)
    if active_domain == "midjourney_v8_1_core":
        domain_complete = "missing_scene_description" in resolved
    else:
        domain_complete = bool(active_domain and active_domain != "system_design_navigation" and "missing_domain_parameters" in resolved)
    if has_scope and has_contract and domain_complete:
        return "EXECUTION"
    if has_scope and has_contract:
        return "DOMAIN_INJECTION"
    if has_scope:
        return "CONTRACTING"
    return "SCOPING"
