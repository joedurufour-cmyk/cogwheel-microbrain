def render_answer(
    response_plan: dict,
    narrative_model: dict,
    implications: dict,
    collision: dict,
    gap_resolution: dict | None = None,
    domain_state: dict | None = None,
) -> str:
    if not response_plan:
        raise Exception("NO_RESPONSE_PLAN")

    gap_resolution = gap_resolution or {}
    domain_state = domain_state or {}
    objective = narrative_model.get("objective") or "no congelado"
    problem = narrative_model.get("active_problem") or "falta contexto operativo"
    risk = (implications.get("risks") or narrative_model.get("current_risks") or ["deriva de sistema"])[0]
    next_move = implications.get("next_best_move") or "definir siguiente movimiento arquitectonico"
    central_objects = narrative_model.get("central_objects") or []
    relations = narrative_model.get("active_relations") or []
    blocking_gap = narrative_model.get("blocking_gap")
    active_domain = domain_state.get("active_domain") or narrative_model.get("active_domain")

    if "missing_io_contract" in gap_resolution.get("resolved_gaps", []):
        modes = narrative_model.get("input_contract", {}).get("mode", [])
        mode_label = " + ".join(mode.replace("_", " ") for mode in modes) or "texto libre"
        return "\n".join(
            [
                "Contrato de entrada actualizado:",
                f"- modo: {mode_label}",
                "",
                "Ya no voy a volver a pedir ese dato.",
                "",
                f"Dominio activo detectado: {format_domain(active_domain)}.",
                "",
                "Objeto central:",
                f"- {(central_objects or ['prompt_generator'])[0]}",
                "",
                "Contrato parcial:",
                f"- input: {mode_label}",
                "- output: pendiente",
                "",
                "Siguiente bloqueo:",
                "definir contrato de salida: quieres que el generador entregue solo prompt final, o prompt + negative prompt + parametros?",
            ]
        )

    if "missing_output_contract" in gap_resolution.get("resolved_gaps", []):
        includes = narrative_model.get("output_contract", {}).get("includes", [])
        include_label = " + ".join(item.replace("_", " ") for item in includes) or "positive prompt"
        return "\n".join(
            [
                "Contrato de salida actualizado:",
                f"- incluye: {include_label}",
                "",
                "Ya no voy a volver a pedir ese dato.",
                "",
                f"Dominio activo detectado: {format_domain(active_domain)}.",
                "",
                "Siguiente bloqueo:",
                "confirmar parametros de dominio: aspect ratio, stylize, chaos/seed si aplican y version Midjourney.",
            ]
        )

    if "missing_domain_parameters" in gap_resolution.get("resolved_gaps", []):
        parameters = domain_state.get("domain_parameters") or {}
        return "\n".join(
            [
                "Parametros de dominio actualizados:",
                f"- aspect ratio: {parameters.get('aspect_ratio') or 'pendiente'}",
                f"- stylize: {parameters.get('stylize') if parameters.get('stylize') is not None else 'pendiente'}",
                f"- chaos: {parameters.get('chaos') if parameters.get('chaos') is not None else 'pendiente'}",
                f"- seed: {parameters.get('seed') if parameters.get('seed') is not None else 'pendiente'}",
                "",
                "Ya no voy a volver a pedir ese dato.",
                "",
                f"Dominio activo detectado: {format_domain(active_domain)}.",
                "",
                "Siguiente movimiento:",
                "generar prompt final Midjourney con positive prompt, negative prompt y parametros.",
            ]
        )

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
        elif blocking_gap == "missing_output_contract":
            lines.extend(
                [
                    "",
                    "Gap bloqueante:",
                    "- missing_output_contract",
                    "",
                    f"Dominio activo detectado: {format_domain(active_domain)}.",
                    "",
                    "Siguiente movimiento:",
                    "Fijar output contract: solo prompt final, o prompt + negative prompt + parametros?",
                ]
            )
        elif blocking_gap == "missing_domain_parameters":
            lines.extend(
                [
                    "",
                    "Gap bloqueante:",
                    "- missing_domain_parameters",
                    "",
                    f"Dominio activo detectado: {format_domain(active_domain)}.",
                    "",
                    "Siguiente movimiento:",
                    "Confirmar aspect ratio, stylize y parametros tecnicos Midjourney.",
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


def format_domain(domain_id: str | None) -> str:
    if domain_id == "midjourney_v8_1_core":
        return "Midjourney v8.1"
    if domain_id:
        return domain_id
    return "ninguno"
