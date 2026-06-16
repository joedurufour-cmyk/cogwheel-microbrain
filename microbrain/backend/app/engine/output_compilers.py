import json
import os


OUTPUT_TYPE_KEYWORDS = {
    "app_stack":       ["stack", "arquitectura", "tech stack", "infraestructura", "servicios", "deployment"],
    "python_code":     ["python", "codigo python", "código python", "script", "clase", "funcion", "modulo"],
    "advanced_prompt": ["prompt", "midjourney", "dalle", "stable diffusion", "imagen", "render", "generate image"],
    "csv":             ["csv", "tabla", "spreadsheet", "excel", "filas", "columnas", "datos"],
    "text":            ["texto", "documento", "articulo", "resumen", "descripcion", "markdown"],
}


def detect_output_type(narrative_state: dict, domain_state: dict) -> str:
    """Infers the desired output type from io_contract and active_domain."""
    output_contract = narrative_state.get("output_contract") or {}
    includes = output_contract.get("includes") or []
    active_domain = domain_state.get("active_domain") or ""
    combined = " ".join(str(i) for i in includes).lower()

    for output_type, keywords in OUTPUT_TYPE_KEYWORDS.items():
        if any(k in combined for k in keywords):
            return output_type

    if "midjourney" in active_domain or "dalle" in active_domain:
        return "advanced_prompt"

    return "text"


def compile_app_stack(narrative_state: dict, domain_state: dict) -> dict:
    objective = narrative_state.get("objective") or "sistema"
    central_objects = narrative_state.get("central_objects") or []
    central = central_objects[0] if central_objects else "app"
    architecture = narrative_state.get("current_architecture") or []
    params = domain_state.get("domain_parameters") or {}

    frontend = params.get("frontend") or ("React + Vite" if "frontend_client" in architecture else "React + Vite")
    backend = params.get("backend") or ("FastAPI" if "backend_api" in architecture else "FastAPI + Python 3.12")
    database = params.get("database") or ("PostgreSQL" if "narrative_database" in architecture else "PostgreSQL")
    deployment = params.get("deployment") or "Render (backend) + Netlify (frontend)"

    services = [s.replace("_", " ") for s in architecture]
    extra_services = [f"- {k}: {v}" for k, v in params.items() if k not in ("frontend", "backend", "database", "deployment")]

    preview = "\n".join([
        f"# Stack: {objective}",
        "",
        "## Capas",
        f"- **Frontend**: {frontend}",
        f"- **Backend**: {backend}",
        f"- **Base de datos**: {database}",
        f"- **Deployment**: {deployment}",
        "",
        f"## Objeto central",
        f"- {central}",
    ])
    if services:
        preview += "\n\n## Servicios detectados\n" + "\n".join(f"- {s}" for s in services)
    if extra_services:
        preview += "\n\n## Parámetros adicionales\n" + "\n".join(extra_services)

    return {
        "artifact_type": "app_stack",
        "stack": {"frontend": frontend, "backend": backend, "database": database, "deployment": deployment},
        "compiled_preview": preview,
    }


def compile_python_code(narrative_state: dict, domain_state: dict) -> dict:
    objective = narrative_state.get("objective") or "sistema"
    central_objects = narrative_state.get("central_objects") or []
    central = central_objects[0] if central_objects else "module"
    params = domain_state.get("domain_parameters") or {}

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        code = _generate_python_with_llm(objective, central, params)
    else:
        code = _python_template(objective, central, params)

    return {
        "artifact_type": "python_code",
        "language": "python",
        "compiled_preview": f"```python\n{code}\n```",
    }


def compile_advanced_prompt(narrative_state: dict, domain_state: dict) -> dict:
    params = domain_state.get("domain_parameters") or {}
    objective = narrative_state.get("objective") or ""
    central = (narrative_state.get("central_objects") or ["system"])[0]
    active_domain = domain_state.get("active_domain") or ""

    # Use captured scene description as prompt base; fall back to LLM generation
    scene = params.get("scene_description") or ""
    if not scene and os.getenv("ANTHROPIC_API_KEY"):
        scene = _generate_midjourney_scene(objective, central, params)
    base = scene or f"{objective} / {central}".strip(" /")

    flags = []
    if params.get("aspect_ratio"):
        flags.append(f"--ar {params['aspect_ratio']}")
    if params.get("stylize"):
        flags.append(f"--s {params['stylize']}")
    version = params.get("version") or "8.1"
    flags.append(f"--v {version}")
    if params.get("chaos") is not None:
        flags.append(f"--chaos {params['chaos']}")
    if params.get("seed") is not None:
        flags.append(f"--seed {params['seed']}")

    platform = active_domain.replace("_core", "").replace("_", " ").title()
    suffix = " ".join(flags)
    compiled = f"{base} {suffix}".strip()
    negative = params.get("negative_prompt", "")

    preview_lines = [
        f"**Plataforma:** {platform}",
        "",
        "**Positive prompt:**",
        "```",
        compiled,
        "```",
    ]
    if negative:
        preview_lines += ["", "**Negative prompt:**", "```", negative, "```"]

    return {
        "artifact_type": "advanced_prompt",
        "platform": platform,
        "positive_prompt": base,
        "negative_prompt": negative,
        "parameters": suffix,
        "compiled_preview": "\n".join(preview_lines),
    }


def compile_text(narrative_state: dict, domain_state: dict) -> dict:
    objective = narrative_state.get("objective") or "sistema"
    central_objects = narrative_state.get("central_objects") or []
    central = central_objects[0] if central_objects else "módulo"
    hypothesis = narrative_state.get("current_hypothesis") or ""
    architecture = narrative_state.get("current_architecture") or []
    params = domain_state.get("domain_parameters") or {}

    sections = [f"# {objective}", "", f"**Objeto central:** {central}"]
    if hypothesis:
        sections += ["", f"**Hipótesis:** {hypothesis}"]
    if architecture:
        sections += ["", "## Arquitectura", *[f"- {a.replace('_', ' ')}" for a in architecture]]
    if params:
        sections += ["", "## Parámetros", *[f"- **{k}**: {v}" for k, v in params.items()]]

    return {
        "artifact_type": "text",
        "compiled_preview": "\n".join(sections),
    }


def compile_csv(narrative_state: dict, domain_state: dict) -> dict:
    params = domain_state.get("domain_parameters") or {}
    objective = narrative_state.get("objective") or "output"
    central_objects = narrative_state.get("central_objects") or []

    if params:
        headers = list(params.keys())
        values = [str(params[h]) if params[h] is not None else "" for h in headers]
        rows = [",".join(headers), ",".join(values)]
    else:
        rows = ["campo,valor", f"objetivo,{objective}"]
        if central_objects:
            rows.append(f"objeto_central,{central_objects[0]}")

    csv_content = "\n".join(rows)
    return {
        "artifact_type": "csv",
        "headers": rows[0].split(","),
        "compiled_preview": f"```csv\n{csv_content}\n```",
    }


def _generate_python_with_llm(objective: str, central: str, params: dict) -> str:
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        params_desc = json.dumps(params, ensure_ascii=False) if params else "ninguno"
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            system=(
                "Eres un generador de código Python. "
                "Genera código limpio con type hints, docstrings cortos y sin comentarios obvios. "
                "Solo devuelve el bloque de código Python puro, sin explicaciones ni markdown."
            ),
            messages=[{
                "role": "user",
                "content": (
                    f"Genera código Python para: {objective}\n"
                    f"Objeto central: {central}\n"
                    f"Parámetros de dominio: {params_desc}"
                ),
            }],
        )
        raw = response.content[0].text.strip()
        if "```" in raw:
            raw = raw.split("```")[1].lstrip("python").strip()
            if "```" in raw:
                raw = raw.split("```")[0].strip()
        return raw
    except Exception:
        return _python_template(objective, central, params)


def _generate_midjourney_scene(objective: str, central: str, params: dict) -> str:
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        context = f"Objetivo: {objective}\nObjeto central: {central}"
        if params:
            skip = {"aspect_ratio", "stylize", "version", "chaos", "seed", "negative_prompt", "scene_description"}
            extras = {k: v for k, v in params.items() if k not in skip}
            if extras:
                context += f"\nDetalles adicionales: {json.dumps(extras, ensure_ascii=False)}"
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            system=(
                "Eres un experto en Midjourney. "
                "Genera SOLO la descripción visual del prompt positivo en inglés: "
                "sujeto, acción, escena, estilo fotográfico, iluminación, atmósfera. "
                "Sin flags técnicos (--ar, --s). Sin explicaciones. Solo el texto del prompt."
            ),
            messages=[{"role": "user", "content": context}],
        )
        return response.content[0].text.strip()
    except Exception:
        return f"{objective} / {central}".strip(" /")


def _python_template(objective: str, central: str, params: dict) -> str:
    class_name = "".join(w.capitalize() for w in central.replace("_", " ").split())
    attrs = "\n".join(f"    {k}: str | None = None" for k in list(params.keys())[:6]) if params else "    data: dict | None = None"
    return f'"""\n{objective}\n"""\nfrom dataclasses import dataclass, field\nfrom typing import Any\n\n\n@dataclass\nclass {class_name}:\n{attrs}\n\n    def compile(self) -> str:\n        raise NotImplementedError\n\n\ndef main() -> None:\n    obj = {class_name}()\n    print(obj.compile())\n\n\nif __name__ == "__main__":\n    main()\n'
