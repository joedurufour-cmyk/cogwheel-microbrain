import os
import uuid

from app.engine.artifact_exporter import OUTPUTS_DIR
from app.engine.platform_compilers import compile_dalle, compile_midjourney, compile_nano_banana
from app.engine.visual_blueprint import parse_blueprint

VALID_PLATFORMS = {"midjourney_v8_1", "dalle_3", "nano_banana"}

_PLATFORM_NEGATIVES = {
    "midjourney_v8_1": (
        "blurry, low quality, distorted, watermark, text overlay, "
        "oversaturated, bad anatomy, cropped, out of frame"
    ),
    "dalle_3": "",
    "nano_banana": "",
}


def compile_mj81(input_text: str, params: dict) -> dict:
    base = input_text.strip()
    if not base:
        return {"status": "EMPTY_INPUT", "message": "input_text is required"}

    platform = params.get("platform", "midjourney_v8_1")
    if platform not in VALID_PLATFORMS:
        platform = "midjourney_v8_1"

    blueprint = parse_blueprint(base)

    if platform == "midjourney_v8_1":
        positive = compile_midjourney(blueprint, params)
    elif platform == "dalle_3":
        positive = compile_dalle(blueprint)
    else:
        positive = compile_nano_banana(blueprint)

    output_mode = params.get("output_mode", "prompt_plus_negative")
    default_negative = _PLATFORM_NEGATIVES.get(platform, "")
    negative = default_negative if (output_mode == "prompt_plus_negative" and default_negative) else ""

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
