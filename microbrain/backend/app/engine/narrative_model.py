from app.engine.kb import has_any, unique


def update_narrative_model(narrative_before: dict, segments: list[dict], raw_input: str = "", object_frame: dict | None = None) -> dict:
    text = raw_input or " ".join(segment["text"] for segment in segments)
    stated_goal = first_role(segments, "objective")
    stated_problem = first_role(segments, "problem")
    constraints = [segment["text"] for segment in segments if segment["role"] == "contract"]
    beliefs = [segment["text"] for segment in segments if segment["role"] == "assumption"]

    objective = infer_objective(text, stated_goal) or narrative_before.get("objective")
    active_problem = infer_problem(text, stated_problem) or narrative_before.get("active_problem")
    architecture = unique((narrative_before.get("current_architecture") or []) + infer_architecture_terms(text))
    risks = unique((narrative_before.get("current_risks") or []) + infer_risks(text))
    loops = unique((narrative_before.get("open_loops") or []) + infer_open_loops(text))
    object_frame = object_frame or {}
    central_objects = object_frame.get("central_objects") or narrative_before.get("central_objects") or []
    active_relations = object_frame.get("active_relations") or narrative_before.get("active_relations") or []
    blocking_gap = object_frame.get("blocking_gap") or narrative_before.get("blocking_gap")

    return {
        "objective": infer_objective_from_objects(text, central_objects) or objective,
        "active_problem": active_problem or infer_problem_from_gap(blocking_gap),
        "central_objects": central_objects,
        "active_relations": active_relations,
        "blocking_gap": blocking_gap,
        "object_graph": object_frame.get("graph_json", {}),
        "current_hypothesis": infer_hypothesis(text) or narrative_before.get("current_hypothesis"),
        "current_architecture": architecture[-12:],
        "current_risks": risks[-12:],
        "open_loops": loops[-12:],
        "decisions": narrative_before.get("decisions") or [],
        "validations": unique((narrative_before.get("validations") or []) + infer_validations(text))[-12:],
        "stated_goal": stated_goal,
        "stated_problem": stated_problem,
        "stated_constraints": constraints,
        "stated_beliefs": beliefs,
        "emotional_signal": "friction" if has_any(text, ["jodido", "frustracion", "preocupa", "no mantiene"]) else "neutral",
    }


def first_role(segments: list[dict], role: str) -> str | None:
    for segment in segments:
        if segment["role"] == role:
            return segment["text"]
    return None


def infer_objective(text: str, stated_goal: str | None) -> str | None:
    if has_any(text, ["constructor de prompts", "generador de prompts", "prompt generator", "prompts para renders"]):
        return "construir un generador de prompts para renders"
    if has_any(text, ["micro cerebro", "motor conversador"]):
        return "construir MicroBrain"
    if has_any(text, ["sistemas verticales"]):
        return "probar Cogwheel en sistemas verticales"
    if has_any(text, ["codigo", "backend", "frontend"]):
        return "llevar Cogwheel a implementacion full stack"
    return stated_goal


def infer_objective_from_objects(text: str, central_objects: list[str]) -> str | None:
    if "prompt_generator" in central_objects and has_any(text, ["render", "renders", "midjourney"]):
        return "construir un generador de prompts para renders"
    return None


def infer_problem_from_gap(blocking_gap: str | None) -> str | None:
    if blocking_gap == "missing_io_contract":
        return "falta contrato input/output del objeto central"
    return None


def infer_problem(text: str, stated_problem: str | None) -> str | None:
    if has_any(text, ["no mantiene el hilo"]):
        return "no mantiene hilo narrativo"
    if has_any(text, ["no validamos", "sin metricas"]):
        return "validacion insuficiente"
    if has_any(text, ["demasiada informacion visible", "mas tabs", "mas debug"]):
        return "diagnostico visible invade UX"
    if has_any(text, ["no es sandbox"]):
        return "contrato reconstruible violado"
    return stated_problem


def infer_architecture_terms(text: str) -> list[str]:
    terms = []
    if has_any(text, ["backend", "api", "fastapi"]):
        terms.append("backend_api")
    if has_any(text, ["frontend", "react", "vite"]):
        terms.append("frontend_client")
    if has_any(text, ["postgres", "database", "memoria"]):
        terms.append("narrative_database")
    if has_any(text, ["engine", "motor", "collision"]):
        terms.append("narrative_collision_engine")
    return terms


def infer_risks(text: str) -> list[str]:
    risks = []
    if has_any(text, ["mas tabs", "mas debug", "demasiada informacion"]):
        risks.append("scope_explosion")
    if has_any(text, ["codigo", "implementar"]) and not has_any(text, ["contrato"]):
        risks.append("implementation_without_design")
    if has_any(text, ["no validamos", "sin metricas"]):
        risks.append("design_without_validation")
    if has_any(text, ["sobreinfiera"]):
        risks.append("over_inference")
    return risks


def infer_open_loops(text: str) -> list[str]:
    loops = []
    if has_any(text, ["siguiente movimiento", "siguiente paso"]):
        loops.append("define_next_architectural_move")
    if has_any(text, ["validar", "metricas", "test"]):
        loops.append("define_validation_cases")
    if has_any(text, ["contrato"]):
        loops.append("freeze_contract")
    return loops


def infer_hypothesis(text: str) -> str | None:
    if has_any(text, ["narrativa original"]):
        return "la narrativa original debe gobernar el build"
    if has_any(text, ["no un chatbot"]):
        return "el producto no debe derivar a chatbot generico"
    return None


def infer_validations(text: str) -> list[str]:
    if has_any(text, ["validar", "metricas", "test", "prueba"]):
        return ["validation_required"]
    return []
