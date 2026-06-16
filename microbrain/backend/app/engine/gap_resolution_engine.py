import re
import unicodedata
from copy import deepcopy


GAP_RESOLUTION_RULES = {
    "missing_io_contract": {
        "detects_resolution_terms": [
            "texto libre",
            "bloques semanticos",
            "bloques semánticos",
            "formulario",
            "campos",
            "input",
            "entrada",
            "output",
            "salida",
        ],
        "write_to": "system_story.io_contract",
        "next_gap": "missing_output_contract",
    },
    "missing_output_contract": {
        "detects_resolution_terms": [
            "prompt final",
            "negative prompt",
            "parametros",
            "parámetros",
            "--ar",
            "--s",
            "--v",
            "json",
            "markdown",
        ],
        "write_to": "system_story.output_contract",
        "next_gap": "missing_domain_parameters",
    },
    "missing_domain_parameters": {
        "detects_resolution_terms": [
            "aspect ratio",
            "stylize",
            "chaos",
            "seed",
            "v 8.1",
            "midjourney",
            "--ar",
            "--s",
            "--v",
            "--chaos",
            "--seed",
            "stack",
            "frontend",
            "backend",
            "python",
            "csv",
        ],
        "write_to": "domain_state.domain_parameters",
        "next_gap": None,
    },
}


def resolve_gaps(raw_input: str, narrative_state: dict, domain_state: dict, contract) -> dict:
    text = normalize(raw_input)
    resolved_before = set(domain_state.get("resolved_gaps") or narrative_state.get("resolved_gaps") or [])
    active_gap = (
        narrative_state.get("blocking_gap")
        or first_unresolved_loop(narrative_state, resolved_before)
        or infer_active_gap(narrative_state, domain_state, resolved_before, contract)
    )

    # Midjourney: scene must be captured before tech params
    _active_domain = domain_state.get("active_domain")
    _has_scene = bool((domain_state.get("domain_parameters") or {}).get("scene_description"))
    if (
        active_gap == "missing_domain_parameters"
        and _active_domain == "midjourney_v8_1_core"
        and not _has_scene
        and "missing_scene_description" not in resolved_before
    ):
        active_gap = "missing_scene_description"

    result = {
        "resolved_gaps": [],
        "active_gap_before": active_gap,
        "blocking_gap": active_gap if active_gap not in resolved_before else None,
        "next_gap": None,
        "input_contract": narrative_state.get("input_contract") or {},
        "output_contract": narrative_state.get("output_contract") or {},
        "domain_parameters": deepcopy(domain_state.get("domain_parameters") or {}),
        "inferred_data": infer_domain_data(text, contract.domain_id),
        "write_to": None,
    }

    if not active_gap or active_gap in resolved_before:
        result["blocking_gap"] = first_unresolved_loop(narrative_state, resolved_before)
        return result

    # Scene description: any substantial text resolves it; flags also captured
    if active_gap == "missing_scene_description":
        domain_params = detect_domain_parameters(text)
        scene = domain_params.get("scene_description") or (raw_input.strip() if len(raw_input.strip()) > 3 else "")
        if scene:
            result["resolved_gaps"].append("missing_scene_description")
            result["write_to"] = "domain_state.domain_parameters"
            merged = {**result["domain_parameters"], **domain_params}
            merged["scene_description"] = merged.get("scene_description") or scene
            result["domain_parameters"] = merged
            result["next_gap"] = None
            result["blocking_gap"] = None
        return result

    rule = GAP_RESOLUTION_RULES.get(active_gap)
    if not rule or not has_resolution_terms(text, rule["detects_resolution_terms"]):
        return result

    result["resolved_gaps"].append(active_gap)
    result["write_to"] = rule["write_to"]
    result["next_gap"] = rule["next_gap"]
    result["blocking_gap"] = rule["next_gap"]

    if active_gap == "missing_io_contract":
        result["input_contract"] = {"mode": detect_input_modes(text)}
    elif active_gap == "missing_output_contract":
        result["output_contract"] = {"includes": detect_output_includes(text)}
    elif active_gap == "missing_domain_parameters":
        result["domain_parameters"] = {**result["domain_parameters"], **detect_domain_parameters(text)}

    return result


def first_unresolved_loop(narrative_state: dict, resolved: set[str]) -> str | None:
    for loop in narrative_state.get("open_loops") or []:
        if loop not in resolved:
            return loop
    return None


def infer_active_gap(narrative_state: dict, domain_state: dict, resolved: set[str], contract=None) -> str | None:
    central_objects = narrative_state.get("central_objects") or []
    prompt_like = any(item in central_objects for item in ["prompt_generator", "render_prompt_generator"])
    active_domain = domain_state.get("active_domain") or narrative_state.get("active_domain")
    if prompt_like and not narrative_state.get("input_contract") and "missing_io_contract" not in resolved:
        return "missing_io_contract"
    if narrative_state.get("input_contract") and not narrative_state.get("output_contract") and "missing_output_contract" not in resolved:
        return "missing_output_contract"
    # Midjourney: require explicit scene before tech params
    if active_domain == "midjourney_v8_1_core" and narrative_state.get("output_contract"):
        has_scene = bool((domain_state.get("domain_parameters") or {}).get("scene_description"))
        if not has_scene and "missing_scene_description" not in resolved:
            return "missing_scene_description"
    if should_request_domain_parameters(active_domain, narrative_state, domain_state, resolved, contract):
        return "missing_domain_parameters"
    return None


def should_request_domain_parameters(
    active_domain: str | None,
    narrative_state: dict,
    domain_state: dict,
    resolved: set[str],
    contract=None,
) -> bool:
    if not active_domain or active_domain == "system_design_navigation":
        return False
    if not narrative_state.get("output_contract"):
        return False
    if "missing_domain_parameters" in resolved:
        return False
    if domain_state.get("domain_parameters"):
        return False
    mandatory_keys = set(getattr(contract, "mandatory_keys", []) or [])
    return bool(mandatory_keys - {"input_mode", "output_format"})


def has_resolution_terms(text: str, terms: list[str]) -> bool:
    normalized_terms = [normalize(term) for term in terms]
    return any(term in text for term in normalized_terms)


def detect_input_modes(text: str) -> list[str]:
    modes = []
    if "texto libre" in text or "free text" in text:
        modes.append("free_text")
    if "bloques semanticos" in text:
        modes.append("semantic_blocks")
    if "formulario" in text or "campos" in text:
        modes.append("form_fields")
    if "input" in text or "entrada" in text:
        modes.append("free_text")
    return ordered_unique(modes or ["free_text"])


def detect_output_includes(text: str) -> list[str]:
    includes = []
    # Output type detection (5 types)
    if any(k in text for k in ["stack", "arquitectura", "tech stack", "infraestructura", "servicios", "deployment"]):
        includes.append("app_stack")
    if any(k in text for k in ["python", "codigo python", "script", "clase", "funcion", "modulo"]):
        includes.append("python_code")
    if any(k in text for k in ["csv", "tabla", "spreadsheet", "excel", "filas", "columnas"]):
        includes.append("csv")
    if any(k in text for k in ["midjourney", "dalle", "stable diffusion", "generar imagen", "generate image"]):
        includes.append("advanced_prompt")
    if any(k in text for k in ["texto", "documento", "articulo", "resumen", "descripcion"]):
        includes.append("text")
    # Legacy prompt sub-fields (kept for backward compat)
    if "prompt final" in text or "positive prompt" in text:
        includes.append("positive_prompt")
    if "negative prompt" in text:
        includes.append("negative_prompt")
    if "parametros" in text or "--ar" in text or "--s" in text or "--v" in text:
        includes.append("technical_parameters")
    return ordered_unique(includes or ["text"])


def detect_domain_parameters(text: str) -> dict:
    parameters = {}
    _FLAG_PATTERNS = [
        (r"(?:--ar|aspect ratio|aspec ratio)\s*(?:=|:)?\s*([0-9]+:[0-9]+)", "aspect_ratio", str),
        (r"(?:--s|stylize)\s*(?:=|:)?\s*([0-9]+)", "stylize", int),
        (r"(?:--v|version)\s*(?:=|:)?\s*([0-9.]+)", "version", str),
        (r"(?:--chaos|--c\b|chaos)\s*(?:=|:)?\s*([0-9]+)", "chaos", int),
        (r"(?:--seed|seed)\s*(?:=|:)?\s*([0-9]+)", "seed", int),
    ]
    consumed = text
    for pattern, key, cast in _FLAG_PATTERNS:
        m = re.search(pattern, consumed)
        if m:
            parameters[key] = cast(m.group(1))
            consumed = consumed[:m.start()] + consumed[m.end():]

    # Collect everything that isn't a flag as scene description
    scene = re.sub(r"[,;]+", ",", consumed).strip(" ,;")
    scene = re.sub(r"\s{2,}", " ", scene).strip()
    if scene and len(scene) > 3:
        parameters["scene_description"] = scene
    return parameters


def infer_domain_data(text: str, domain_id: str) -> list[str]:
    if domain_id != "midjourney_v8_1_core":
        return []
    data = []
    if "arquitectura" in text or "architecture" in text:
        data.append("architecture_render")
    if "cinematic" in text or "cinematico" in text or "cinematicos" in text:
        data.append("cinematic_candidate_aspect_ratio")
    if "producto" in text or "product render" in text:
        data.append("clean_studio_lighting")
    return data


def normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value.lower())
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


def ordered_unique(items: list[str]) -> list[str]:
    result = []
    for item in items:
        if item and item not in result:
            result.append(item)
    return result
