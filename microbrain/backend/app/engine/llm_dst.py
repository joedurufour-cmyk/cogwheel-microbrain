import json
import os
import re

CODEX_SYSTEM_PROMPT = """Eres un Orquestador Agnóstico de Diseño de Sistemas y un Rastreador del Estado del Diálogo (Dialogue State Tracker).
Tu única función es extraer, acumular y estructurar la información del usuario siguiendo una Máquina de Estados estricta.

REGLA DE ORO (ANTI-AMNESIA):
Eres un sistema "stateless" (sin memoria inherente). Si un valor del estado (como el 'objective' o el 'io_contract') ya fue definido en turnos anteriores y el usuario envía un bloque de texto nuevo (ej. parámetros técnicos o descripciones), DEBES conservar el valor anterior o devolver "none" para esa llave. NUNCA sobrescribas ni borres el progreso anterior con valores vacíos si el usuario no te ordenó cambiarlo.

MÁQUINA DE ESTADOS (PROGRESIÓN PASO A PASO):
Evalúa el mensaje del usuario. Avanza fase por fase de manera lineal. NUNCA retrocedas a una fase anterior si los datos ya fueron recolectados.

PASO 1: Identifica el 'objective' (¿Qué quiere construir?) y el 'central_object' (El nodo o sistema principal).
-> Si faltan, tu 'next_move' debe ser preguntar por ellos. Si ya están, pasa al Paso 2.

PASO 2: Define el 'io_contract_input' (El formato de entrada, ej. texto libre) y el 'io_contract_output' (Lo que se espera que salga).
Los 5 tipos de output válidos son: "app_stack" (arquitectura/tech stack), "python_code" (código Python), "advanced_prompt" (prompt para plataforma como Midjourney/DALL-E), "text" (texto/documento) y "csv" (datos en CSV). Asigna el tipo correcto según lo que pida el usuario.
-> Si faltan, tu 'next_move' debe ser definir el contrato. Si ya están, pasa al Paso 3.

PASO 3: El usuario insertará reglas o datos de un dominio específico (ej. midjourney_v8_1_core, leyes, variables). Extrae CUALQUIER parámetro técnico, sufijo (ej. --ar, --s) o bloque de descripción que el usuario envíe y guárdalo exclusivamente en el arreglo 'domain_parameters'.

PASO 4: Cuando el objetivo, el contrato y los parámetros del dominio estén capturados:
-> Cambia 'blocking_gap' a "none".
-> Cambia 'next_move' ESTRICTAMENTE a la orden: "EXECUTE_DOMAIN_COMPILER".
-> NO hagas más preguntas. NO pidas más confirmaciones.

FORMATO DE SALIDA (JSON ESTRICTO):
Tu respuesta debe ser únicamente un objeto JSON válido con las siguientes llaves exactas. No incluyas texto fuera del JSON.
{
  "objective": "string (El objetivo extraído, o 'none' si no se menciona en este turno)",
  "central_object": "string (El objeto central, o 'none')",
  "active_domain": "string (El nombre del dominio si aplica, o 'none')",
  "io_contract_input": "string (El formato de entrada, o 'none')",
  "io_contract_output": "string (El formato de salida, o 'none')",
  "domain_parameters": ["lista de strings extrayendo los sufijos o descripciones del dominio"],
  "blocking_gap": "string (SOLO uno de estos valores exactos: 'missing_io_contract', 'missing_output_contract', 'missing_domain_parameters', o 'none' si el Paso 4 se cumple)",
  "next_move": "string (La siguiente instrucción al usuario, o 'EXECUTE_DOMAIN_COMPILER' si el Paso 4 se cumple)"
}"""

_EMPTY = {"none", "None", "NONE", "no congelado", "No congelado", "", None}


def run_llm_dst(user_input: str, current_state: dict) -> dict | None:
    """
    Calls Claude with the Codex as system prompt.
    Returns a dict matching the Codex JSON schema, or None if unavailable.
    The caller merges the result with persisted state via state_reducers.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=CODEX_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": _build_context(user_input, current_state)}],
        )
        raw = response.content[0].text.strip()
        if "```" in raw:
            raw = raw.split("```")[1].lstrip("json").strip()
        return json.loads(raw)
    except Exception:
        return None


def build_universal_state(narrative: dict, domain_state: dict) -> dict:
    """Extracts universal state fields from narrative + domain state for the LLM context."""
    return {
        "objective": narrative.get("objective"),
        "central_object": (narrative.get("central_objects") or [None])[0],
        "active_domain": domain_state.get("active_domain") or narrative.get("active_domain"),
        "io_contract": {
            "input": narrative.get("input_contract"),
            "output": narrative.get("output_contract"),
        },
        "domain_parameters": domain_state.get("domain_parameters") or {},
        "blocking_gap": narrative.get("blocking_gap"),
        "next_move": domain_state.get("next_action_prompt") or "",
    }


def apply_llm_dst_to_gap_resolution(
    llm_output: dict,
    gap_resolution: dict,
    domain_state: dict,
) -> dict:
    """
    Merges LLM DST output into the gap_resolution dict.
    The LLM output takes priority for blocking_gap, io contracts, and domain parameters.
    resolved_gaps accumulates — never shrinks.
    """
    result = dict(gap_resolution)
    resolved = list(result.get("resolved_gaps") or [])

    next_move = llm_output.get("next_move") or ""
    blocking_gap_raw = llm_output.get("blocking_gap") or ""
    _CANONICAL_GAPS = {"missing_io_contract", "missing_output_contract", "missing_domain_parameters"}
    blocking_gap = blocking_gap_raw if blocking_gap_raw in _CANONICAL_GAPS else ""
    io_input = llm_output.get("io_contract_input") or ""
    io_output = llm_output.get("io_contract_output") or ""
    domain_params_raw = llm_output.get("domain_parameters") or []

    if next_move == "EXECUTE_DOMAIN_COMPILER":
        for gap in ("missing_io_contract", "missing_output_contract", "missing_domain_parameters"):
            if gap not in resolved:
                resolved.append(gap)
        result["blocking_gap"] = None
        # Still extract domain parameters — this turn may contain scene content or flags
        if domain_params_raw:
            extracted = _parse_domain_parameters(domain_params_raw)
            if extracted:
                existing = dict(domain_state.get("domain_parameters") or {})
                existing.update(extracted)
                result["domain_parameters"] = existing
        result["resolved_gaps"] = resolved
        return result

    if blocking_gap and blocking_gap not in _EMPTY:
        result["blocking_gap"] = blocking_gap

    if io_input and io_input not in _EMPTY:
        result["input_contract"] = {"mode": [io_input]}
        if "missing_io_contract" not in resolved:
            resolved.append("missing_io_contract")

    if io_output and io_output not in _EMPTY:
        result["output_contract"] = {"includes": [io_output]}
        if "missing_output_contract" not in resolved:
            resolved.append("missing_output_contract")

    if domain_params_raw:
        extracted = _parse_domain_parameters(domain_params_raw)
        if extracted:
            existing = dict(domain_state.get("domain_parameters") or {})
            existing.update(extracted)
            result["domain_parameters"] = existing
            if "missing_domain_parameters" not in resolved:
                resolved.append("missing_domain_parameters")

    result["resolved_gaps"] = resolved
    return result


def _build_context(user_input: str, state: dict) -> str:
    lines = ["Estado actual acumulado del sistema:"]
    if state.get("objective"):
        lines.append(f'- objective: {state["objective"]}')
    if state.get("central_object"):
        lines.append(f'- central_object: {state["central_object"]}')
    domain = state.get("active_domain")
    if domain and domain != "system_design_navigation":
        lines.append(f'- active_domain: {domain}')
    io = state.get("io_contract") or {}
    if io.get("input"):
        lines.append(f'- io_contract_input: {io["input"]}')
    if io.get("output"):
        lines.append(f'- io_contract_output: {io["output"]}')
    params = state.get("domain_parameters") or {}
    if params:
        lines.append(f'- domain_parameters: {json.dumps(params, ensure_ascii=False)}')
    lines.append("")
    lines.append(f"Nuevo mensaje del usuario:\n{user_input}")
    return "\n".join(lines)


def _parse_domain_parameters(raw: list) -> dict:
    result = {}
    descriptive: list[str] = []
    for item in raw:
        if not isinstance(item, str):
            continue
        item = item.strip()
        if not item or item in _EMPTY:
            continue
        matched = False
        ar = re.search(r"(?:--ar|ar)\s+([0-9]+:[0-9]+)", item, re.IGNORECASE)
        if ar:
            result["aspect_ratio"] = ar.group(1)
            matched = True
        s_match = re.search(r"(?:--s|stylize)\s+([0-9]+)", item, re.IGNORECASE)
        if s_match:
            result["stylize"] = int(s_match.group(1))
            matched = True
        v_match = re.search(r"--v\s+([0-9.]+)", item, re.IGNORECASE)
        if v_match:
            result["version"] = v_match.group(1)
            matched = True
        chaos = re.search(r"(?:--chaos|--c)\s+([0-9]+)", item, re.IGNORECASE)
        if chaos:
            result["chaos"] = int(chaos.group(1))
            matched = True
        seed = re.search(r"--seed\s+([0-9]+)", item, re.IGNORECASE)
        if seed:
            result["seed"] = int(seed.group(1))
            matched = True
        if not matched and ":" in item:
            key, _, value = item.partition(":")
            key = key.strip().lstrip("-").replace(" ", "_").lower()
            if key:
                result[key] = value.strip()
                matched = True
        if not matched:
            descriptive.append(item)
    if descriptive:
        existing = result.get("scene_description", "")
        joined = ", ".join(descriptive)
        result["scene_description"] = f"{existing}, {joined}".strip(", ") if existing else joined
    return result
