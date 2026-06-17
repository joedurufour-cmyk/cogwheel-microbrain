import os
import uuid

from app.engine.artifact_exporter import OUTPUTS_DIR
from app.engine.platform_compilers import compile_dalle, compile_midjourney, compile_nano_banana
from app.engine.style_presets import STYLE_PRESETS, apply_style_preset
from app.engine.visual_blueprint import parse_blueprint

VALID_PLATFORMS = {"midjourney_v8_1", "dalle_3", "nano_banana"}

# Only Midjourney supports a --no negative prompt flag; DALL-E and Nano
# Banana are natural-language platforms with no negative-prompt concept.
_PLATFORMS_WITH_NEGATIVE = {"midjourney_v8_1"}


def _normalize_platform(params: dict) -> str:
    platform = params.get("platform", "midjourney_v8_1")
    return platform if platform in VALID_PLATFORMS else "midjourney_v8_1"


def _compile_positive(blueprint: dict, platform: str, params: dict) -> str:
    if platform == "midjourney_v8_1":
        return compile_midjourney(blueprint, params)
    if platform == "dalle_3":
        return compile_dalle(blueprint)
    return compile_nano_banana(blueprint)


def _compile_negative(blueprint: dict, platform: str, params: dict) -> str:
    output_mode = params.get("output_mode", "prompt_plus_negative")
    default_negative = blueprint["negative"] if platform in _PLATFORMS_WITH_NEGATIVE else ""
    return default_negative if (output_mode == "prompt_plus_negative" and default_negative) else ""


def compile_mj81(input_text: str, params: dict) -> dict:
    base = input_text.strip()
    if not base:
        return {"status": "EMPTY_INPUT", "message": "input_text is required"}

    platform = _normalize_platform(params)
    blueprint = parse_blueprint(base)

    positive = _compile_positive(blueprint, platform, params)
    negative = _compile_negative(blueprint, platform, params)

    canvas = _render_canvas(positive, negative)
    file_meta = _save_txt(positive, negative)

    return {
        "status": "DONE_WITH_PROMPT",
        "positive_prompt": positive,
        "negative_prompt": negative,
        "canvas": canvas,
        "file": file_meta,
        "platform": platform,
        "blueprint": blueprint,
    }


def compile_mj81_all_styles(input_text: str, params: dict) -> dict:
    """Compile the same Kernel into all 6 fixed output-style presets at once."""
    base = input_text.strip()
    if not base:
        return {"status": "EMPTY_INPUT", "message": "input_text is required"}

    platform = _normalize_platform(params)
    blueprint = parse_blueprint(base)

    variants = []
    for preset in STYLE_PRESETS:
        styled_blueprint = apply_style_preset(blueprint, preset)
        positive = _compile_positive(styled_blueprint, platform, params)
        negative = _compile_negative(styled_blueprint, platform, params)
        variants.append({
            "style_id": preset["id"],
            "style_label": preset["label"],
            "positive_prompt": positive,
            "negative_prompt": negative,
            "canvas": _render_canvas(positive, negative),
        })

    return {
        "status": "DONE_WITH_VARIANTS",
        "platform": platform,
        "variants": variants,
        "blueprint": blueprint,
    }


def _render_canvas(positive: str, negative: str) -> str:
    parts = [f"POSITIVE PROMPT\n{positive}"]
    if negative:
        parts.append(f"NEGATIVE PROMPT\n{negative}")
    return "\n\n".join(parts)


def _save_txt(positive: str, negative: str) -> dict:
    filename = f"mj81_{uuid.uuid4().hex[:8]}.txt"
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    path = os.path.join(OUTPUTS_DIR, filename)
    content = positive
    if negative:
        content += f"\n\nNEGATIVE PROMPT:\n{negative}"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return {
        "filename": filename,
        "path": path,
        "download_url": f"/outputs/{filename}",
    }
