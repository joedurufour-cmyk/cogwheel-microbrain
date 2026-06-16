from app.engine.answer_renderer import render_answer
from app.engine.collision_engine import detect_collision
from app.engine.dialogue_state_tracker import update_narrative_with_dialogue_state
from app.engine.domain_compiler import domain_compiler_node, execute_next_move
from app.engine.domain_contract_router import detect_domain, load_domain_contract
from app.engine.domain_state_tracker import detect_anticipation_gaps, empty_domain_state, update_domain_state
from app.engine.gap_resolution_engine import resolve_gaps
from app.engine.implication_engine import infer_implications
from app.engine.intent_reader import infer_intent
from app.engine.kb import TEST_INPUTS
from app.engine.mental_model import update_mental_model
from app.engine.narrative_model import update_narrative_model
from app.engine.object_extractor import extract_objects
from app.engine.process import empty_narrative
from app.engine.relationship_graph import build_relationship_graph
from app.engine.response_planner import build_response_plan
from app.engine.segmenter import segment
from app.engine.state_reducers import keep_if_empty, merge_dicts


def run_engine(raw_input: str, before=None):
    narrative_before = before or empty_narrative()
    segments = segment(raw_input)
    extraction = extract_objects(raw_input, segments)
    graph = build_relationship_graph(narrative_before, extraction)
    narrative = update_narrative_model(narrative_before, segments, raw_input, graph)
    mental = update_mental_model(narrative_before, segments, raw_input)
    intent = infer_intent(raw_input, segments)
    collision = detect_collision(narrative_before, narrative, mental, intent)
    implications = infer_implications(narrative, collision, intent)
    plan = build_response_plan(intent, collision, implications)
    answer = render_answer(plan, narrative, implications, collision)
    return {"segments": segments, "extraction": extraction, "graph": graph, "narrative": narrative, "collision": collision, "plan": plan, "answer": answer}


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


def test_object_extractor_prompt_generator_case():
    result = run_engine("Constructor de prompts para renders")
    assert "prompt_generator" in result["narrative"]["central_objects"]
    assert any(
        relation["subject"] == "prompt_generator"
        and relation["predicate"] == "generates"
        and relation["object"] == "render_prompts"
        for relation in result["narrative"]["active_relations"]
    )
    assert result["narrative"]["blocking_gap"] == "missing_io_contract"
    assert "prompt_generator" in result["answer"]
    assert "define system objective" not in result["answer"]


def run_domain_turn(raw_input: str, narrative_before=None, domain_state_before=None):
    narrative_before = narrative_before or empty_narrative()
    domain_state_before = domain_state_before or empty_domain_state()
    narrative_before = {**narrative_before, "domain_state": domain_state_before}
    segments = segment(raw_input)
    extraction = extract_objects(raw_input, segments)
    active_domain = detect_domain(raw_input, extraction, narrative_before)
    contract = load_domain_contract(active_domain)
    graph = build_relationship_graph({**narrative_before, "resolved_gaps": domain_state_before.get("resolved_gaps", [])}, extraction)
    narrative = update_narrative_model(narrative_before, segments, raw_input, graph)
    gap_resolution = resolve_gaps(raw_input, narrative, domain_state_before, contract)
    domain_state = update_domain_state(domain_state_before, active_domain, gap_resolution, extraction, contract)
    anticipation = detect_anticipation_gaps(domain_state, contract, gap_resolution.get("inferred_data", []))
    domain_state["anticipation_gaps"] = anticipation["anticipation_gaps"]
    narrative = update_narrative_with_dialogue_state(
        narrative,
        narrative_before,
        gap_resolution,
        anticipation,
        domain_state,
    )
    return {
        "narrative": narrative,
        "domain_state": domain_state,
        "gap_resolution": gap_resolution,
        "anticipation": anticipation,
        "contract": contract.model_dump(),
    }


def test_detect_midjourney_domain_contract():
    result = run_domain_turn("Quiero construir un generador de prompts para renders Midjourney v8.1")
    assert result["domain_state"]["active_domain"] == "midjourney_v8_1_core"
    assert "prompt_generator" in result["narrative"]["central_objects"]
    assert result["narrative"]["blocking_gap"] == "missing_io_contract"
    assert result["contract"]["domain_id"] == "midjourney_v8_1_core"


def test_resolve_input_contract_advances_gap():
    before = run_domain_turn("Quiero construir un generador de prompts para renders Midjourney v8.1")
    result = run_domain_turn("Input texto libre y bloques semánticos", before["narrative"], before["domain_state"])
    assert "missing_io_contract" in result["domain_state"]["resolved_gaps"]
    assert result["narrative"]["input_contract"] == {"mode": ["free_text", "semantic_blocks"]}
    assert result["narrative"]["blocking_gap"] == "missing_output_contract"


def test_do_not_repeat_resolved_input_gap():
    first = run_domain_turn("Quiero construir un generador de prompts para renders Midjourney v8.1")
    second = run_domain_turn("Input texto libre y bloques semánticos", first["narrative"], first["domain_state"])
    third = run_domain_turn("Usaremos metodología Kimi 2.6", second["narrative"], second["domain_state"])
    assert third["narrative"]["blocking_gap"] == "missing_output_contract"
    assert third["narrative"]["blocking_gap"] != "missing_io_contract"


def test_resolve_output_contract_advances_to_scene_description():
    first = run_domain_turn("Quiero construir un generador de prompts para renders Midjourney v8.1")
    second = run_domain_turn("Input texto libre y bloques semánticos", first["narrative"], first["domain_state"])
    third = run_domain_turn(
        "El output debe ser prompt final, negative prompt y parámetros --ar --s --v 8.1",
        second["narrative"],
        second["domain_state"],
    )
    assert "missing_output_contract" in third["domain_state"]["resolved_gaps"]
    assert third["narrative"]["output_contract"] == {
        "includes": ["positive_prompt", "negative_prompt", "technical_parameters"]
    }
    # Midjourney now advances to scene description, not domain parameters directly
    assert third["narrative"]["blocking_gap"] == "missing_scene_description"


def test_negative_prompt_does_not_replace_prompt_generator_as_central_object():
    first = run_domain_turn("Quiero construir un generador de prompts para renders Midjourney v8.1")
    second = run_domain_turn("Input texto libre y bloques semánticos", first["narrative"], first["domain_state"])
    third = run_domain_turn(
        "El output debe ser prompt final, negative prompt y parámetros --ar --s --v 8.1",
        second["narrative"],
        second["domain_state"],
    )
    collision = {"exists": False, "type": None, "severity": 0, "evidence": []}
    implications = infer_implications(third["narrative"], collision, {"explicit": None})
    assert third["narrative"]["central_objects"][0] == "prompt_generator"
    # After output contract, Midjourney asks for scene (not tech params)
    assert implications["next_best_move"] == "describir la escena visual que quieres visualizar"
    assert implications["next_best_move"] != "define system objective"


def test_scene_description_triggers_compilation():
    first = run_domain_turn("Quiero construir un generador de prompts para renders Midjourney v8.1")
    second = run_domain_turn("Input texto libre y bloques semánticos", first["narrative"], first["domain_state"])
    third = run_domain_turn(
        "El output debe ser prompt final, negative prompt y parámetros --ar --s --v 8.1",
        second["narrative"],
        second["domain_state"],
    )
    # Turn 4: scene + optional flags in same message
    fourth = run_domain_turn(
        "supergirl en armadura táctica, ciudad cyberpunk de noche --ar 16:9 --s 200 --v 8.1",
        third["narrative"],
        third["domain_state"],
    )
    collision = {"exists": False, "type": None, "severity": 0, "evidence": []}
    implications = infer_implications(fourth["narrative"], collision, {"explicit": None})
    assert "missing_scene_description" in fourth["domain_state"]["resolved_gaps"]
    assert "supergirl" in fourth["domain_state"]["domain_parameters"]["scene_description"]
    assert fourth["domain_state"]["domain_parameters"]["aspect_ratio"] == "16:9"
    assert fourth["domain_state"]["domain_parameters"]["stylize"] == 200
    assert fourth["narrative"]["phase"] == "EXECUTION"
    assert fourth["narrative"]["active_problem"] is None
    assert fourth["domain_state"]["next_action_prompt"] == "EXECUTE_DOMAIN_COMPILER"
    assert implications["next_best_move"] == "EXECUTE_DOMAIN_COMPILER"
    compiled = domain_compiler_node(fourth["narrative"], fourth["domain_state"], load_domain_contract("midjourney_v8_1_core"))
    assert compiled["status"] == "compiled"
    assert compiled["schema_name"] == "midjourney_v8_1_core_Schema"
    assert compiled["output_envelope"]["artifact_type"] == "prompt_package"
    preview = compiled["output_envelope"]["deliverables"][0]["compiled_preview"]
    assert "supergirl" in preview
    assert "--ar 16:9" in preview
    assert "--s 200" in preview
    assert "--v 8.1" in preview


def test_universal_state_machine_executes_non_midjourney_domain():
    narrative = empty_narrative()
    narrative.update(
        {
            "objective": "construir generador de contratos de alquiler",
            "central_objects": ["contract_generator"],
            "input_contract": {"mode": ["free_text"]},
            "output_contract": {"includes": ["legal_contract", "clause_summary"]},
            "active_domain": "legal_contracts_core",
            "resolved_gaps": ["missing_io_contract", "missing_output_contract", "missing_domain_parameters"],
        }
    )
    domain_state = {
        **empty_domain_state(),
        "active_domain": "legal_contracts_core",
        "domain_parameters": {"penalty_clause": "required", "deposit_months": 2},
        "resolved_gaps": ["missing_io_contract", "missing_output_contract", "missing_domain_parameters"],
    }
    updated = update_narrative_with_dialogue_state(
        narrative,
        narrative,
        {"resolved_gaps": [], "blocking_gap": None},
        {"anticipation_gaps": [], "inferred_data": []},
        domain_state,
    )
    collision = {"exists": False, "type": None, "severity": 0, "evidence": []}
    implications = infer_implications(updated, collision, {"explicit": None})
    compiled = domain_compiler_node(
        updated,
        {**domain_state, "next_action_prompt": "EXECUTE_DOMAIN_COMPILER"},
        load_domain_contract("system_design_navigation"),
    )
    assert updated["phase"] == "EXECUTION"
    assert updated["blocking_gap"] is None
    assert updated["active_problem"] is None
    assert implications["next_best_move"] == "EXECUTE_DOMAIN_COMPILER"
    assert compiled["status"] == "compiled"
    assert compiled["output_envelope"]["artifact_type"] == "document_package"
    assert compiled["output_envelope"]["next_runtime_action"] == "EXECUTE_OUTPUT_RENDERER"
    assert compiled["validated_data"] == {"penalty_clause": "required", "deposit_months": 2}


def test_state_reducers_preserve_historical_values_against_none_updates():
    assert keep_if_empty("construir un generador de prompts", "none") == "construir un generador de prompts"
    assert keep_if_empty("construir un generador de prompts", "no congelado") == "construir un generador de prompts"
    assert merge_dicts(
        {"input": ["free_text"], "output": ["positive_prompt"]},
        {"input": "none", "parameters": ["--ar 5:11"]},
    ) == {"input": ["free_text"], "output": ["positive_prompt"], "parameters": ["--ar 5:11"]}


def test_system_design_compiler_executes():
    result = execute_next_move({
        "next_move": "EXECUTE_DOMAIN_COMPILER",
        "active_domain": "system_design_navigation",
        "objective": "sistema de gestion de inventario",
        "central_object": "inventory_manager",
        "output_contract": {"includes": ["app_stack"]},
        "input_contract": {"mode": ["free_text"]},
        "parameters": {"frontend": "React", "backend": "FastAPI", "database": "PostgreSQL"},
    })
    assert result["type"] == "compiled_output"
    assert result["next_move"] == "DONE"
    assert result["domain"] == "system_design_navigation"
    content = result["content"]
    assert content["artifact_type"] == "app_stack"
    assert "React" in content["compiled_preview"]
    assert "FastAPI" in content["compiled_preview"]
    assert "PostgreSQL" in content["compiled_preview"]


def test_execute_next_move_no_action_when_not_execute():
    result = execute_next_move({"next_move": "AWAIT_INPUT"})
    assert result["type"] == "no_action"
    assert result["next_move"] == "AWAIT_INPUT"


def test_anticipate_midjourney_domain_parameters():
    first = run_domain_turn("Quiero construir un generador de prompts para renders Midjourney v8.1")
    second = run_domain_turn("Input texto libre y bloques semánticos", first["narrative"], first["domain_state"])
    third = run_domain_turn(
        "El output debe ser prompt final, negative prompt y parámetros --ar --s --v 8.1",
        second["narrative"],
        second["domain_state"],
    )
    fourth = run_domain_turn("Será para renders cinemáticos de arquitectura", third["narrative"], third["domain_state"])
    assert "architecture_render" in fourth["anticipation"]["inferred_data"]
    assert "cinematic_candidate_aspect_ratio" in fourth["anticipation"]["inferred_data"]
    assert "confirm_aspect_ratio" in fourth["anticipation"]["anticipation_gaps"]
    assert "confirm_stylization_level" in fourth["anticipation"]["anticipation_gaps"]
