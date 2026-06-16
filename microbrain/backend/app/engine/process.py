import json
import os
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session as DbSession

from app import models
from app.engine.answer_renderer import render_answer
from app.engine.collision_engine import detect_collision
from app.engine.dialogue_state_tracker import update_narrative_with_dialogue_state
from app.engine.domain_compiler import domain_compiler_node
from app.engine.domain_contract_router import detect_domain, load_domain_contract
from app.engine.domain_state_tracker import (
    detect_anticipation_gaps,
    load_domain_state,
    persist_domain_state,
    update_domain_state,
)
from app.engine.gap_resolution_engine import resolve_gaps
from app.engine.llm_dst import apply_llm_dst_to_gap_resolution, build_universal_state, run_llm_dst
from app.engine.implication_engine import infer_implications
from app.engine.intent_reader import infer_intent
from app.engine.mental_model import update_mental_model
from app.engine.narrative_model import update_narrative_model
from app.engine.object_extractor import extract_objects
from app.engine.relationship_graph import build_relationship_graph
from app.engine.report_builder import build_report
from app.engine.response_planner import build_response_plan
from app.engine.segmenter import segment
from app.engine.state_reducers import append_unique, keep_if_empty, merge_dicts

SESSION_TTL_HOURS = int(os.getenv("SESSION_TTL_HOURS", "24"))
MAX_OPEN_LOOPS = int(os.getenv("MAX_OPEN_LOOPS", "3"))
MAX_ACTIVE_RISKS = int(os.getenv("MAX_ACTIVE_RISKS", "8"))
MAX_ACTIVE_RELATIONS = int(os.getenv("MAX_ACTIVE_RELATIONS", "12"))


def process_turn(db: DbSession, session_id: int, raw_input: str) -> dict:
    session = db.get(models.Session, session_id)
    if session:
        age_hours = (datetime.now(timezone.utc) - session.created_at.replace(tzinfo=timezone.utc)).total_seconds() / 3600
        if age_hours > SESSION_TTL_HOURS:
            raise HTTPException(status_code=410, detail="session_expired")

    narrative_before = load_narrative(db, session_id)
    domain_state_before = load_domain_state(db, session_id)
    narrative_before["domain_state"] = domain_state_before
    narrative_before["active_domain"] = domain_state_before.get("active_domain")
    narrative_before["resolved_gaps"] = domain_state_before.get("resolved_gaps", [])

    segments = segment(raw_input)
    object_extraction = extract_objects(raw_input, segments)
    active_domain = detect_domain(raw_input, object_extraction, narrative_before)
    domain_contract = load_domain_contract(active_domain)
    relationship_graph = build_relationship_graph(narrative_before, object_extraction)
    narrative_model = update_narrative_model(narrative_before, segments, raw_input, relationship_graph)
    mental_model = update_mental_model(narrative_before, segments, raw_input)
    intent = infer_intent(raw_input, segments)

    gap_resolution = resolve_gaps(
        raw_input=raw_input,
        narrative_state=narrative_model,
        domain_state=domain_state_before,
        contract=domain_contract,
    )
    llm_output = run_llm_dst(raw_input, build_universal_state(narrative_before, domain_state_before))
    if llm_output:
        gap_resolution = apply_llm_dst_to_gap_resolution(llm_output, gap_resolution, domain_state_before)
        # Propagate LLM-extracted objective when the rule-based model missed it
        _empty = {"none", "no congelado", ""}
        if (llm_output.get("objective") or "").lower().strip() not in _empty:
            narrative_model["objective"] = narrative_model.get("objective") or llm_output["objective"]
        if (llm_output.get("central_object") or "").lower().strip() not in _empty:
            co = llm_output["central_object"]
            if co not in narrative_model.get("central_objects", []):
                narrative_model["central_objects"] = [co] + (narrative_model.get("central_objects") or [])

    updated_domain_state = update_domain_state(
        domain_state_before, active_domain, gap_resolution, object_extraction, domain_contract,
    )
    anticipation = detect_anticipation_gaps(
        updated_domain_state, domain_contract, gap_resolution.get("inferred_data", []),
    )
    updated_domain_state["anticipation_gaps"] = anticipation.get("anticipation_gaps", [])

    narrative_model = update_narrative_with_dialogue_state(
        narrative_model, narrative_before, gap_resolution, anticipation, updated_domain_state,
    )
    # State pruning: cap growing lists to avoid long-session drift
    narrative_model["open_loops"] = narrative_model.get("open_loops", [])[:MAX_OPEN_LOOPS]
    narrative_model["current_risks"] = narrative_model.get("current_risks", [])[:MAX_ACTIVE_RISKS]
    narrative_model["active_relations"] = narrative_model.get("active_relations", [])[:MAX_ACTIVE_RELATIONS]

    collision = detect_collision(narrative_before, narrative_model, mental_model, intent)
    implications = infer_implications(narrative_model, collision, intent)
    compiled_domain = domain_compiler_node(narrative_model, updated_domain_state, domain_contract)

    # Transition next_action_prompt after successful compilation so it doesn't stay frozen
    if compiled_domain.get("status") == "compiled":
        updated_domain_state["next_action_prompt"] = "OUTPUT_RENDERED"

    response_plan = build_response_plan(intent, collision, implications)
    if not response_plan:
        raise HTTPException(status_code=500, detail="no_response_plan")

    answer = render_answer(
        response_plan, narrative_model, implications, collision,
        gap_resolution, updated_domain_state, compiled_domain, llm_output,
    )

    turn = models.Turn(session_id=session_id, raw_input=raw_input, answer=answer)
    db.add(turn)
    db.flush()
    apply_turn_id_to_relations(str(turn.id), object_extraction, relationship_graph, narrative_model)

    # Persist report to DB for /reports endpoint (not returned in turn response)
    report = build_report(
        raw_input, narrative_before, narrative_model, segments, mental_model, intent,
        collision, implications, response_plan, answer, object_extraction, relationship_graph,
        gap_resolution, updated_domain_state, domain_contract.model_dump(), anticipation, compiled_domain,
    )

    persist_narrative(db, session_id, narrative_model)
    persist_domain_state(db, session_id, updated_domain_state)
    db.add(models.TurnReport(turn_id=turn.id, report_json=json.dumps(report)))
    if collision["exists"]:
        db.add(models.Collision(
            session_id=session_id, turn_id=turn.id,
            collision_type=collision["type"], severity=collision["severity"],
            evidence_json=json.dumps(collision["evidence"]),
        ))
    db.commit()
    db.refresh(turn)

    pipeline_trace = {
        "INPUT_RECEIVED": bool(raw_input),
        "DOMAIN_ROUTED": active_domain,
        "NEXT_MOVE_SELECTED": updated_domain_state.get("next_action_prompt"),
        "COMPILER_STATUS": compiled_domain.get("status"),
    }

    return {
        "id": turn.id,
        "raw_input": raw_input,
        "answer": answer,
        "report": report,
        "narrative_model": narrative_model,
        "collision_detection": collision,
        "implication_engine": implications,
        "response_plan": response_plan,
        "gap_resolution": gap_resolution,
        "domain_state": updated_domain_state,
        "compiled_domain": compiled_domain,
        "llm_dst": llm_output,
        "pipeline_trace": pipeline_trace,
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
        "active_relations": json.loads(state.active_relations_json or "[]")[:MAX_ACTIVE_RELATIONS],
        "blocking_gap": state.blocking_gap,
        "object_graph": {
            "objects": json.loads(state.central_objects_json or "[]"),
            "relations": json.loads(state.active_relations_json or "[]")[:MAX_ACTIVE_RELATIONS],
            "gaps": [{"type": state.blocking_gap, "blocking": True}] if state.blocking_gap else [],
        },
        "current_architecture": json.loads(state.current_architecture_json or "[]"),
        "current_risks": json.loads(state.current_risks_json or "[]")[:MAX_ACTIVE_RISKS],
        "open_loops": json.loads(state.open_loops_json or "[]")[:MAX_OPEN_LOOPS],
        "decisions": json.loads(state.decisions_json or "[]"),
        "validations": json.loads(state.validations_json or "[]"),
        "input_contract": json.loads(state.input_contract_json or "{}"),
        "output_contract": json.loads(state.output_contract_json or "{}"),
        "resolved_gaps": json.loads(state.resolved_gaps_json or "[]"),
        "active_domain": state.active_domain,
        "anticipation_gaps": json.loads(state.anticipation_gaps_json or "[]"),
    }


def persist_narrative(db: DbSession, session_id: int, narrative: dict) -> None:
    state = db.query(models.NarrativeState).filter(models.NarrativeState.session_id == session_id).one_or_none()
    if not state:
        state = models.NarrativeState(session_id=session_id)
        db.add(state)
    previous_central_objects = json.loads(state.central_objects_json or "[]")
    previous_active_relations = json.loads(state.active_relations_json or "[]")
    previous_input_contract = json.loads(state.input_contract_json or "{}")
    previous_output_contract = json.loads(state.output_contract_json or "{}")
    previous_resolved_gaps = json.loads(state.resolved_gaps_json or "[]")
    previous_anticipation_gaps = json.loads(state.anticipation_gaps_json or "[]")

    state.objective = keep_if_empty(state.objective, narrative.get("objective"))
    state.active_problem = keep_if_empty(state.active_problem, narrative.get("active_problem"))
    state.central_objects_json = json.dumps(append_unique(previous_central_objects, narrative.get("central_objects", [])))
    state.active_relations_json = json.dumps(
        merge_relations_for_state(previous_active_relations, narrative.get("active_relations", []))[:MAX_ACTIVE_RELATIONS]
    )
    state.blocking_gap = narrative.get("blocking_gap")
    state.current_hypothesis = keep_if_empty(state.current_hypothesis, narrative.get("current_hypothesis"))
    state.current_architecture_json = json.dumps(
        append_unique(json.loads(state.current_architecture_json or "[]"), narrative.get("current_architecture", []))
    )
    state.current_risks_json = json.dumps(
        append_unique(json.loads(state.current_risks_json or "[]"), narrative.get("current_risks", []))[:MAX_ACTIVE_RISKS]
    )
    state.open_loops_json = json.dumps(narrative.get("open_loops", [])[:MAX_OPEN_LOOPS])
    state.decisions_json = json.dumps(append_unique(json.loads(state.decisions_json or "[]"), narrative.get("decisions", [])))
    state.validations_json = json.dumps(append_unique(json.loads(state.validations_json or "[]"), narrative.get("validations", [])))
    state.input_contract_json = json.dumps(merge_dicts(previous_input_contract, narrative.get("input_contract", {})))
    state.output_contract_json = json.dumps(merge_dicts(previous_output_contract, narrative.get("output_contract", {})))
    state.resolved_gaps_json = json.dumps(append_unique(previous_resolved_gaps, narrative.get("resolved_gaps", [])))
    state.active_domain = keep_if_empty(state.active_domain, narrative.get("active_domain"))
    state.anticipation_gaps_json = json.dumps(
        append_unique(previous_anticipation_gaps, narrative.get("anticipation_gaps", []))
    )


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
        "input_contract": {},
        "output_contract": {},
        "resolved_gaps": [],
        "active_domain": None,
        "anticipation_gaps": [],
    }


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


def merge_relations_for_state(previous: list[dict], current: list[dict]) -> list[dict]:
    merged = []
    seen = set()
    for relation in previous + current:
        key = (relation.get("subject"), relation.get("predicate"), relation.get("object"))
        if key not in seen:
            seen.add(key)
            merged.append(relation)
    return merged
