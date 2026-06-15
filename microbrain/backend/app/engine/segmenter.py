import re

from app.engine.kb import has_any


def segment(raw_input: str) -> list[dict]:
    parts = [
        part.strip()
        for part in re.split(r"(?<=[.!?])\s+|\s+(?:pero|aunque|y|sin|porque|para)\s+", raw_input.strip())
        if part.strip()
    ]
    return [{"text": part, "role": classify_segment(part)} for part in parts or [raw_input.strip()]]


def classify_segment(text: str) -> str:
    if has_any(text, ["quiero", "necesito", "construir", "probar", "implementar"]):
        return "objective"
    if has_any(text, ["no mantiene", "no es", "falta", "demasiada", "preocupa", "problema"]):
        return "problem"
    if has_any(text, ["contrato", "debe", "sin perder", "reconstruible", "no debe"]):
        return "contract"
    if has_any(text, ["codigo", "backend", "frontend", "deploy", "produccion"]):
        return "implementation_step"
    if has_any(text, ["validar", "metricas", "test", "prueba"]):
        return "validation"
    return "assumption"
