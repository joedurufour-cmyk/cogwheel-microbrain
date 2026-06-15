import json

from sqlalchemy.orm import Session as DbSession

from app import models
from app.engine.answer_renderer import render_answer
from app.engine.collision_engine import detect_collision
from app.engine.implication_engine import infer_implications
from app.engine.intent_reader import infer_intent
from app.engine.mental_model import update_mental_model
from app.engine.narrative_model import update_narrative_model
from app.engine.report_builder import build_report
from app.engine.response_planner import build_response_plan
from app.engine.segmenter import segment


def process_turn(db: DbSession, session_id: int, raw_input: str) -> dict:
    narrative_before = load_narrative(db, session_id)
    segments = segment(raw_input)
    narrative_model = update_narrative_model(narrative_before, segments, raw_input)
    mental_model = update_mental_model(narrative_before, segments, raw_input)
    intent = infer_intent(raw_input, segments)
    collision = detect_collision(narrative_before, narrative_model, mental_model, intent)
    implications = infer_implications(narrative_model, collision, intent)
    response_plan = build_response_plan(intent, collision, implications)
    if not response_plan:
        raise Exception("NO_RESPONSE_PLAN")
    answer = render_answer(response_plan, narrative_model, implications, collision)
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
    )

    turn = models.Turn(session_id=session_id, raw_input=raw_input, answer=answer)
    db.add(turn)
    db.flush()

    persist_narrative(db, session_id, narrative_model)
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
        "current_architecture": [],
        "current_risks": [],
        "open_loops": [],
        "decisions": [],
        "validations": [],
    }
