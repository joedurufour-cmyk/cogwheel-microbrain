from app.engine.answer_renderer import render_answer
from app.engine.collision_engine import detect_collision
from app.engine.implication_engine import infer_implications
from app.engine.intent_reader import infer_intent
from app.engine.kb import TEST_INPUTS
from app.engine.mental_model import update_mental_model
from app.engine.narrative_model import update_narrative_model
from app.engine.process import empty_narrative
from app.engine.response_planner import build_response_plan
from app.engine.segmenter import segment


def run_engine(raw_input: str, before=None):
    narrative_before = before or empty_narrative()
    segments = segment(raw_input)
    narrative = update_narrative_model(narrative_before, segments, raw_input)
    mental = update_mental_model(narrative_before, segments, raw_input)
    intent = infer_intent(raw_input, segments)
    collision = detect_collision(narrative_before, narrative, mental, intent)
    implications = infer_implications(narrative, collision, intent)
    plan = build_response_plan(intent, collision, implications)
    answer = render_answer(plan, narrative, implications, collision)
    return {"segments": segments, "narrative": narrative, "collision": collision, "plan": plan, "answer": answer}


def test_all_kb_cases_have_plan_answer_and_no_generic_fallback():
    for raw_input in TEST_INPUTS:
        result = run_engine(raw_input)
        assert result["plan"]
        assert result["answer"]
        assert "Continua" not in result["answer"]
        assert "Dime mas" not in result["answer"]


def test_required_collisions():
    assert run_engine("agreguemos mas tabs para ver todo")["collision"]["type"] == "scope_explosion"
    assert run_engine("esto no es sandbox, debe ser reconstruible")["collision"]["type"] == "contract_violation"
    assert run_engine("estamos agregando cosas pero no validamos")["collision"]["type"] == "design_without_validation"
    before = empty_narrative()
    before["objective"] = "construir chatbot general"
    assert run_engine("la narrativa original era construir un motor, no un chatbot", before)["collision"]["type"] == "goal_drift"
