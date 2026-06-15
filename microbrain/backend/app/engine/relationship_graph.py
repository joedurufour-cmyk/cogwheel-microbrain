from datetime import datetime, timezone

from app.engine.object_extractor import canonicalize


def build_relationship_graph(narrative_before: dict, extraction: dict) -> dict:
    previous_objects = narrative_before.get("central_objects") or []
    extracted_objects = ordered_unique(
        extraction.get("products", [])
        + extraction.get("systems", [])
        + extraction.get("modules", [])
        + extraction.get("entities", [])
    )
    central_objects = ordered_unique(extracted_objects + previous_objects)[:12]
    relations = merge_relations(narrative_before.get("active_relations") or [], extraction.get("relations") or [])
    gaps = detect_gaps(central_objects, relations, extraction, narrative_before)

    return {
        "central_objects": central_objects,
        "active_relations": relations[:24],
        "gaps": gaps,
        "blocking_gap": next((gap["type"] for gap in gaps if gap.get("blocking")), None),
        "graph_json": {
            "objects": central_objects,
            "relations": relations[:24],
            "aliases": extraction.get("aliases", {}),
            "gaps": gaps,
        },
    }


def merge_relations(previous: list[dict], current: list[dict]) -> list[dict]:
    merged = []
    seen = set()
    for relation in current + previous:
        normalized = {
            **relation,
            "subject": canonicalize(relation.get("subject", "")),
            "object": canonicalize(relation.get("object", "")),
            "valid_from": relation.get("valid_from") or datetime.now(timezone.utc).isoformat(),
            "valid_to": relation.get("valid_to"),
        }
        key = (normalized["subject"], normalized["predicate"], normalized["object"])
        if key not in seen:
            seen.add(key)
            merged.append(normalized)
    return merged


def detect_gaps(central_objects: list[str], relations: list[dict], extraction: dict, narrative_before: dict | None = None) -> list[dict]:
    narrative_before = narrative_before or {}
    gaps = []
    prompt_like = any(item in central_objects for item in ["prompt_generator", "render_prompt_generator"])
    has_output = any(relation["predicate"] == "generates" for relation in relations)
    has_input_contract = any("input" in constraint.lower() or "entra" in constraint.lower() for constraint in extraction.get("constraints", []))
    resolved_gaps = set(narrative_before.get("resolved_gaps") or [])
    has_persisted_input_contract = bool(narrative_before.get("input_contract"))

    if prompt_like and has_output and not has_input_contract and not has_persisted_input_contract and "missing_io_contract" not in resolved_gaps:
        gaps.append(
            {
                "type": "missing_io_contract",
                "blocking": True,
                "repair_question": "Para construirlo necesito fijar el contrato minimo: ¿el input sera texto libre, formulario por campos o bloques semanticos?",
            }
        )
    return gaps


def ordered_unique(items: list[str]) -> list[str]:
    result = []
    for item in items:
        if item and item not in result:
            result.append(item)
    return result
