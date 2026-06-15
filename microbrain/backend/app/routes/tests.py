from fastapi import APIRouter

from app.engine.kb import TEST_INPUTS
from app.engine.process import empty_narrative
from app.engine.segmenter import segment
from app.engine.narrative_model import update_narrative_model
from app.engine.object_extractor import extract_objects
from app.engine.relationship_graph import build_relationship_graph
from app.engine.mental_model import update_mental_model
from app.engine.intent_reader import infer_intent
from app.engine.collision_engine import detect_collision
from app.engine.implication_engine import infer_implications
from app.engine.response_planner import build_response_plan
from app.engine.answer_renderer import render_answer
from app.engine.report_builder import build_report

router = APIRouter()


@router.post("/tests/run")
def run_tests():
    results = []
    for index, raw_input in enumerate(TEST_INPUTS, start=1):
        before = empty_narrative()
        segments = segment(raw_input)
        extraction = extract_objects(raw_input, segments)
        graph = build_relationship_graph(before, extraction)
        narrative = update_narrative_model(before, segments, raw_input, graph)
        mental = update_mental_model(before, segments, raw_input)
        intent = infer_intent(raw_input, segments)
        collision = detect_collision(before, narrative, mental, intent)
        implications = infer_implications(narrative, collision, intent)
        plan = build_response_plan(intent, collision, implications)
        answer = render_answer(plan, narrative, implications, collision)
        report = build_report(raw_input, before, narrative, segments, mental, intent, collision, implications, plan, answer, extraction, graph)
        passed = bool(plan and answer and report) and "Continua" not in answer and "Dime mas" not in answer
        if "tabs" in raw_input or "debug" in raw_input:
            passed = passed and collision["type"] == "scope_explosion"
        if "sandbox" in raw_input:
            passed = passed and collision["type"] == "contract_violation"
        if "no validamos" in raw_input:
            passed = passed and collision["type"] == "design_without_validation"
        if "prompt" in raw_input.lower() or "renders" in raw_input.lower() or "midjourney" in raw_input.lower():
            passed = passed and bool(narrative.get("central_objects")) and bool(narrative.get("active_relations") or extraction.get("relations"))
        results.append(
            {
                "index": index,
                "input": raw_input,
                "passed": passed,
                "collision": collision["type"],
                "move": plan["move"],
                "central_objects": narrative.get("central_objects", []),
            }
        )

    failed = [result for result in results if not result["passed"]]
    return {"total": len(results), "passed": len(results) - len(failed), "failed": len(failed), "failed_cases": failed}
