import json

from sqlalchemy.orm import Session as DbSession

from app import models
from app.engine.answer_renderer import render_answer
from app.engine.collision_engine import detect_collision
from app.engine.implication_engine import infer_implications
from app.engine.intent_reader import infer_intent
from app.engine.mental_model import update_mental_model
from app.engine.narrative_model import update_narrative_model
from app.engine.object_extractor import extract_objects
from app.engine.relationship_graph import build_relationship_graph
from app.engine.report_builder import build_report
from app.engine.response_planner import build_response_plan
from app.engine.segmenter import segment


def process_turn(db: DbSession, session_id: int, raw_input: str) -> dict:
    narrative_before = load_narrative(db, session_id)
    segments = segment(raw_input)
    object_extraction = extract_objects(raw_input, segments)
    relationship_graph = build_relationship_graph(narrative_before, object_extraction)
    narrative_model = update_narrative_model(narrative_before, segments, raw_input, relationship_graph)
    mental_model = update_mental_model(narrative_before, segments, raw_input)
    intent = infer_intent(raw_input, segments)
    collision = detect_collision(narrative_before, narrative_model, mental_model, intent)
    implications = infer_implications(narrative_model, collision, intent)
    response_plan = build_response_plan(intent, collision, implications)
    if not response_plan:
        raise Exception("NO_RESPONSE_PLAN")
    answer = render_answer(response_plan, narrative_model, implications, collision)

    turn = models.Turn(session_id=session_id, raw_input=raw_input, answer=answer)
    db.add(turn)
    db.flush()
    apply_turn_id_to_relations(str(turn.id), object_extraction, relationship_graph, narrative_model)

    report = build_report(
        raw_input,
        narrative_before,
        narrative_model,
        segments,
        mental_model,
        intent,
        collision,
        implications,
        response_plan,
        answer,
        object_extraction,
        relationship_graph,
    )

    persist_narrative(db, session_id, narrative_model)
    persist_objects_and_relations(db, session_id, object_extraction, relationship_graph, str(turn.id))
    db.add(models.TurnReport(turn_id=turn.id, report_json=json.dumps(report)))
    if collision["exists"]:
        db.add(
            models.Collision(
                session_id=session_id,
                turn_id=turn.id,
                collision_type=collision["type"],
                severity=collision["severity"],
                evidence_json=json.dumps(collision["evidence"]),
            )
        )
    db.commit()
    db.refresh(turn)

    return {
        "id": turn.id,
        "raw_input": raw_input,
        "segments": segments,
        "narrative_model": narrative_model,
        "object_extraction": object_extraction,
        "relationship_graph": relationship_graph,
        "mental_model": mental_model,
        "inferred_intent": intent,
        "collision_detection": collision,
        "implication_engine": implications,
        "response_plan": response_plan,
        "answer": answer,
        "report": report,
    }


def load_narrative(db: DbSession, session_id: int) -> dict:
    state = db.query(models.NarrativeState).filter(models.NarrativeState.session_id == session_id).one_or_none()
    if not state:
        return empty_narrative()
    return {
        "objective": state.objective,
        "active_problem": state.active_problem,
        "current_hypothesis": state.current_hypothesis,
        "central_objects": json.loads(state.central_objects_json or "[]"),
        "active_relations": json.loads(state.active_relations_json or "[]"),
        "blocking_gap": state.blocking_gap,
        "object_graph": {
            "objects": json.loads(state.central_objects_json or "[]"),
            "relations": json.loads(state.active_relations_json or "[]"),
            "gaps": [{"type": state.blocking_gap, "blocking": True}] if state.blocking_gap else [],
        },
        "current_architecture": json.loads(state.current_architecture_json or "[]"),
        "current_risks": json.loads(state.current_risks_json or "[]"),
        "open_loops": json.loads(state.open_loops_json or "[]"),
        "decisions": json.loads(state.decisions_json or "[]"),
        "validations": json.loads(state.validations_json or "[]"),
    }


def persist_narrative(db: DbSession, session_id: int, narrative: dict) -> None:
    state = db.query(models.NarrativeState).filter(models.NarrativeState.session_id == session_id).one_or_none()
    if not state:
        state = models.NarrativeState(session_id=session_id)
        db.add(state)
    state.objective = narrative.get("objective")
    state.active_problem = narrative.get("active_problem")
    state.central_objects_json = json.dumps(narrative.get("central_objects", []))
    state.active_relations_json = json.dumps(narrative.get("active_relations", []))
    state.blocking_gap = narrative.get("blocking_gap")
    state.current_hypothesis = narrative.get("current_hypothesis")
    state.current_architecture_json = json.dumps(narrative.get("current_architecture", []))
    state.current_risks_json = json.dumps(narrative.get("current_risks", []))
    state.open_loops_json = json.dumps(narrative.get("open_loops", []))
    state.decisions_json = json.dumps(narrative.get("decisions", []))
    state.validations_json = json.dumps(narrative.get("validations", []))


def empty_narrative() -> dict:
    return {
        "objective": None,
        "active_problem": None,
        "current_hypothesis": None,
        "central_objects": [],
        "active_relations": [],
        "blocking_gap": None,
        "object_graph": {"objects": [], "relations": [], "gaps": []},
        "current_architecture": [],
        "current_risks": [],
        "open_loops": [],
        "decisions": [],
        "validations": [],
    }


def persist_objects_and_relations(db: DbSession, session_id: int, extraction: dict, graph: dict, turn_id: str) -> None:
    aliases = extraction.get("aliases", {})
    typed_objects = []
    for object_type, key in [
        ("entity", "entities"),
        ("product", "products"),
        ("system", "systems"),
        ("module", "modules"),
        ("constraint", "constraints"),
        ("dependency", "dependencies"),
        ("action", "actions"),
    ]:
        for canonical_name in extraction.get(key, []):
            typed_objects.append((canonical_name, object_type))

    for canonical_name, object_type in typed_objects:
        existing = (
            db.query(models.DomainObject)
            .filter(models.DomainObject.session_id == session_id, models.DomainObject.canonical_name == canonical_name)
            .one_or_none()
        )
        if not existing:
            existing = models.DomainObject(session_id=session_id, canonical_name=canonical_name, object_type=object_type)
            db.add(existing)
        existing.object_type = object_type
        existing.aliases_json = json.dumps(aliases.get(canonical_name, []))
        existing.properties_json = json.dumps({"source": "object_extractor"})

    for relation in graph.get("active_relations", []):
        existing_relation = (
            db.query(models.ObjectRelation)
            .filter(
                models.ObjectRelation.session_id == session_id,
                models.ObjectRelation.subject == relation["subject"],
                models.ObjectRelation.predicate == relation["predicate"],
                models.ObjectRelation.object == relation["object"],
                models.ObjectRelation.valid_to.is_(None),
            )
            .one_or_none()
        )
        if not existing_relation:
            db.add(
                models.ObjectRelation(
                    session_id=session_id,
                    subject=relation["subject"],
                    predicate=relation["predicate"],
                    object=relation["object"],
                    confidence=relation.get("confidence", 0.6),
                    source_turn_id=turn_id,
                    valid_from=relation.get("valid_from") or turn_id,
                    valid_to=relation.get("valid_to"),
                )
            )


def apply_turn_id_to_relations(turn_id: str, extraction: dict, graph: dict, narrative: dict) -> None:
    for relation_list in [
        extraction.get("relations", []),
        graph.get("active_relations", []),
        graph.get("graph_json", {}).get("relations", []),
        narrative.get("active_relations", []),
        narrative.get("object_graph", {}).get("relations", []),
    ]:
        for relation in relation_list:
            relation["source_turn_id"] = relation.get("source_turn_id") or turn_id
            relation["valid_from"] = relation.get("valid_from") or turn_id
