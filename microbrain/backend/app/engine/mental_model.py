from app.engine.kb import has_any


def update_mental_model(narrative_before: dict, segments: list[dict], raw_input: str) -> dict:
    return {
        "salience": infer_salience(raw_input),
        "load": infer_load(segments, raw_input),
        "repair_needed": has_any(raw_input, ["corrige", "no mantiene", "no es", "jodido", "demasiada"]),
        "reasoning_pattern": infer_reasoning_pattern(raw_input),
        "non_clinical_note": "patterns are conversational inference only",
    }


def infer_salience(text: str) -> list[str]:
    salience = []
    if has_any(text, ["contrato", "sandbox", "reconstruible"]):
        salience.append("contract")
    if has_any(text, ["codigo", "implementacion"]):
        salience.append("implementation")
    if has_any(text, ["validar", "metricas"]):
        salience.append("validation")
    if has_any(text, ["narrativa", "hilo"]):
        salience.append("narrative")
    return salience


def infer_load(segments: list[dict], text: str) -> str:
    if len(segments) >= 4 or has_any(text, ["mezclando", "diseno, validacion, codigo"]):
        return "high"
    if len(segments) >= 2:
        return "medium"
    return "low"


def infer_reasoning_pattern(text: str) -> str:
    if has_any(text, ["mezclando", "asociaciones"]):
        return "associative"
    if has_any(text, ["siguiente", "paso"]):
        return "sequential_planning"
    return "system_navigation"
