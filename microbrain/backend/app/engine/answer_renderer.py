def render_answer(response_plan: dict, narrative_model: dict, implications: dict, collision: dict) -> str:
    if not response_plan:
        raise Exception("NO_RESPONSE_PLAN")

    objective = narrative_model.get("objective") or "no congelado"
    problem = narrative_model.get("active_problem") or "falta contexto operativo"
    risk = (implications.get("risks") or narrative_model.get("current_risks") or ["deriva de sistema"])[0]
    next_move = implications.get("next_best_move") or "definir siguiente movimiento arquitectonico"

    if collision.get("exists"):
        first_line = f"Detecto una colision de {collision['type']}: {collision['evidence'][0] if collision.get('evidence') else 'hay tension de sistema'}."
    else:
        first_line = "No detecto una colision fuerte todavia; falta fijar mejor el contrato narrativo."

    return "\n".join(
        [
            first_line,
            "",
            "Narrativa actual:",
            f"- objetivo: {objective}",
            f"- problema activo: {problem}",
            f"- riesgo: {risk}",
            "",
            "Siguiente movimiento:",
            next_move,
        ]
    )
