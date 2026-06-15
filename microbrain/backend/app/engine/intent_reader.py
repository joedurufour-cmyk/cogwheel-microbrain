from app.engine.kb import has_any


def infer_intent(raw_input: str, segments: list[dict]) -> dict:
    explicit = None
    if has_any(raw_input, ["construir", "crear"]):
        explicit = "build system"
    if has_any(raw_input, ["auditar", "analiza", "revisa"]):
        explicit = "audit system"
    if has_any(raw_input, ["corrige", "no mantiene", "no es sandbox"]):
        explicit = "repair architecture"
    if has_any(raw_input, ["codigo", "implementar"]):
        explicit = "move to implementation"
    if has_any(raw_input, ["validar", "probar", "metricas"]):
        explicit = "validate engine"
    if has_any(raw_input, ["siguiente movimiento", "siguiente paso"]):
        explicit = "choose next move"

    latent = explicit
    if not latent and has_any(raw_input, ["hilo", "narrativa"]):
        latent = "preserve narrative continuity"
    if not latent and has_any(raw_input, ["sobreinfiera"]):
        latent = "limit over inference"
    if not latent and len(segments) >= 3:
        latent = "decompose mixed system request"

    confidence = 0.82 if explicit else 0.62 if latent else 0.42
    return {"explicit": explicit, "latent": latent, "confidence": confidence}
