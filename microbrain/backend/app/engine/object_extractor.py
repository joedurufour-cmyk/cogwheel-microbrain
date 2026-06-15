import re

ALLOWED_PREDICATES = {
    "creates",
    "generates",
    "requires",
    "depends_on",
    "modifies",
    "validates",
    "blocks",
    "replaces",
    "contains",
    "belongs_to",
    "conflicts_with",
    "implements",
    "tests",
    "deploys_to",
}

CANONICAL_ALIASES = {
    "prompt generator": "prompt_generator",
    "constructor de prompts": "prompt_generator",
    "generador de prompts": "prompt_generator",
    "render generator": "render_prompt_generator",
    "prompts para renders": "render_prompt_generator",
    "micro cerebro": "microbrain",
    "backend": "backend_api",
    "fastapi": "backend_api",
    "frontend": "frontend_app",
    "netlify": "frontend_deploy",
    "postgres": "persistent_memory",
}

TYPE_HINTS = {
    "prompt_generator": "product",
    "render_prompt_generator": "system",
    "render_prompt_system": "system",
    "render_prompts": "product",
    "midjourney": "product",
    "backend_api": "system",
    "frontend_app": "system",
    "frontend_deploy": "system",
    "persistent_memory": "system",
    "microbrain": "system",
    "kb_styles": "dependency",
    "templates": "module",
    "variables": "module",
    "final_output": "product",
    "negative_prompt": "product",
    "parameters": "product",
}

ACTION_PATTERNS = {
    "create": ["crear", "construir", "hacer", "build", "constructor", "generador"],
    "modify": ["modificar", "cambiar", "reordenar", "transformar", "replace", "replaces"],
    "validate": ["validar", "probar", "test", "tests"],
    "deploy": ["deploy", "desplegar", "netlify", "render"],
    "remove": ["quitar", "eliminar", "remove"],
}

CONSTRAINT_WORDS = ["debe", "sin", "no quiero", "requiere", "tiene que", "contrato", "v7", "v8", "v8.1"]
DEPENDENCY_WORDS = ["depende", "requiere", "usa", "conecta", "guarda", "maneja"]


def extract_objects(raw_input: str, segments: list[dict] | None = None, source_turn_id: str | None = None) -> dict:
    text = normalize_text(raw_input)
    objects: dict[str, dict] = {}
    relations = []

    for alias, canonical in CANONICAL_ALIASES.items():
        if alias in text:
            add_object(objects, canonical, alias, TYPE_HINTS.get(canonical, "entity"))

    if "midjourney" in text:
        add_object(objects, "midjourney", "Midjourney", "product")
    if re.search(r"\brenders?\b", text):
        add_object(objects, "render_prompts", "renders", "product")
        add_object(objects, "render_prompt_system", "renders", "system")
    if "plantillas" in text or "templates" in text:
        add_object(objects, "templates", "plantillas", "module")
    if "variables" in text:
        add_object(objects, "variables", "variables", "module")
    if "salida final" in text or "output" in text:
        add_object(objects, "final_output", "salida final", "product")
    if "negative prompt" in text:
        add_object(objects, "negative_prompt", "negative prompt", "product")
    if "parametros" in text or "parámetros" in text:
        add_object(objects, "parameters", "parametros", "product")
    if "kb de estilos" in text or "kb estilos" in text:
        add_object(objects, "kb_styles", "KB de estilos", "dependency")

    if ("constructor de prompts" in text or "generador de prompts" in text or "prompt generator" in text) and "renders" in text:
        add_object(objects, "prompt_generator", "constructor de prompts", "product")
        add_object(objects, "render_prompts", "renders", "product")
        relations.append(make_relation("prompt_generator", "generates", "render_prompts", 0.86, source_turn_id))
    if "render_prompt_generator" in objects and "render_prompts" in objects:
        relations.append(make_relation("render_prompt_generator", "generates", "render_prompts", 0.84, source_turn_id))

    if "midjourney" in text and ("prompt" in text or "prompts" in text):
        subject = "prompt_generator" if "prompt_generator" in objects else "render_prompt_generator"
        add_object(objects, subject, subject, TYPE_HINTS.get(subject, "system"))
        relations.append(make_relation(subject, "generates", "render_prompts", 0.82, source_turn_id))
        relations.append(make_relation("render_prompts", "belongs_to", "midjourney", 0.74, source_turn_id))

    if "plantillas" in text or "templates" in text:
        relations.append(make_relation("prompt_generator", "contains", "templates", 0.76, source_turn_id))
    if "variables" in text:
        relations.append(make_relation("prompt_generator", "contains", "variables", 0.76, source_turn_id))
    if "backend" in text and "memoria" in text:
        relations.append(make_relation("backend_api", "depends_on", "persistent_memory", 0.82, source_turn_id))
    if "frontend" in text and "netlify" in text:
        relations.append(make_relation("frontend_app", "deploys_to", "frontend_deploy", 0.88, source_turn_id))
    if "kb de estilos" in text or "kb estilos" in text:
        relations.append(make_relation("prompt_generator", "depends_on", "kb_styles", 0.84, source_turn_id))
    if "negative prompt" in text:
        relations.append(make_relation("prompt_generator", "generates", "negative_prompt", 0.8, source_turn_id))
    if "parametros" in text or "parámetros" in text:
        relations.append(make_relation("prompt_generator", "generates", "parameters", 0.8, source_turn_id))

    actions = [action for action, words in ACTION_PATTERNS.items() if any(word in text for word in words)]
    constraints = extract_phrases(raw_input, CONSTRAINT_WORDS)
    dependencies = extract_phrases(raw_input, DEPENDENCY_WORDS)

    return {
        "entities": names_by_type(objects, "entity"),
        "products": names_by_type(objects, "product"),
        "systems": names_by_type(objects, "system"),
        "modules": names_by_type(objects, "module"),
        "constraints": constraints,
        "dependencies": dependencies,
        "actions": actions,
        "relations": dedupe_relations([relation for relation in relations if relation["predicate"] in ALLOWED_PREDICATES]),
        "aliases": alias_map(objects),
    }


def normalize_text(value: str) -> str:
    return value.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")


def add_object(objects: dict, canonical: str, alias: str, object_type: str) -> None:
    canonical = canonicalize(canonical)
    item = objects.setdefault(canonical, {"canonical_name": canonical, "object_type": object_type, "aliases": []})
    if alias and alias not in item["aliases"]:
        item["aliases"].append(alias)


def canonicalize(term: str) -> str:
    normalized = normalize_text(term).strip()
    if normalized in CANONICAL_ALIASES:
        return CANONICAL_ALIASES[normalized]
    return re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")


def make_relation(subject: str, predicate: str, object_name: str, confidence: float, source_turn_id: str | None) -> dict:
    return {
        "subject": canonicalize(subject),
        "predicate": predicate,
        "object": canonicalize(object_name),
        "confidence": confidence,
        "source_turn_id": source_turn_id,
        "valid_from": source_turn_id,
        "valid_to": None,
    }


def names_by_type(objects: dict, object_type: str) -> list[str]:
    return sorted(name for name, item in objects.items() if item["object_type"] == object_type)


def alias_map(objects: dict) -> dict:
    return {name: item["aliases"] for name, item in objects.items() if item["aliases"]}


def dedupe_relations(relations: list[dict]) -> list[dict]:
    seen = set()
    result = []
    for relation in relations:
        key = (relation["subject"], relation["predicate"], relation["object"])
        if key not in seen:
            seen.add(key)
            result.append(relation)
    return result


def extract_phrases(raw_input: str, markers: list[str]) -> list[str]:
    text = normalize_text(raw_input)
    if not any(marker in text for marker in markers):
        return []
    parts = re.split(r"[.;\n]", raw_input)
    return [part.strip() for part in parts if any(marker in normalize_text(part) for marker in markers)][:5]
