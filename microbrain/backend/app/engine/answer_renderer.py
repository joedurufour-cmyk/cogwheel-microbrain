def render_answer(response_plan: dict, narrative_model: dict, implications: dict, collision: dict) -> str:
    if not response_plan:
        raise Exception("NO_RESPONSE_PLAN")

    objective = narrative_model.get("objective") or "no congelado"
    problem = narrative_model.get("active_problem") or "falta contexto operativo"
    risk = (implications.get("risks") or narrative_model.get("current_risks") or ["deriva de sistema"])[0]
    next_move = implications.get("next_best_move") or "definir siguiente movimiento arquitectonico"
    central_objects = narrative_model.get("central_objects") or []
    relations = narrative_model.get("active_relations") or []
    blocking_gap = narrative_model.get("blocking_gap")

    if central_objects:
        central = central_objects[0]
        key_relation = relations[0] if relations else None
        output = key_relation.get("object") if key_relation and key_relation.get("predicate") == "generates" else None
        lines = [
            f"Objetivo detectado: {objective}.",
            "",
            "Objeto central:",
            f"- {central}",
        ]
        if output:
            lines.extend(["", "Salida esperada:", f"- {output}"])
        if key_relation:
            lines.extend(
                [
                    "",
                    "Relacion clave:",
                    f"- {key_relation['subject']} {key_relation['predicate']} {key_relation['object']}",
                ]
            )
        if blocking_gap == "missing_io_contract":
            lines.extend(
                [
                    "",
                    "Gap bloqueante:",
                    "- missing_io_contract",
                    "",
                    "Siguiente movimiento:",
                    "Para construirlo necesito fijar el contrato minimo: ¿el input sera texto libre, formulario por campos o bloques semanticos?",
                ]
            )
        else:
            lines.extend(["", "Siguiente movimiento:", next_move])
        return "\n".join(lines)

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
