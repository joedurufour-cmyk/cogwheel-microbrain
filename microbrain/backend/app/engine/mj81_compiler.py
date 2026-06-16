import os
import uuid

from app.engine.artifact_exporter import OUTPUTS_DIR

_PLATFORM_ENHANCERS = {
    "midjourney_v8_1": [
        "cinematic composition",
        "high visual clarity",
        "detailed subject",
        "dramatic lighting",
        "rich atmosphere",
        "professional render",
    ],
    "dalle_3": [
        "highly detailed",
        "photorealistic",
        "dramatic lighting",
        "professional photography",
        "rich atmosphere",
    ],
    "nano_banana": [
        "vibrant colors",
        "stylized illustration",
        "bold composition",
        "imaginative scene",
        "editorial quality",
    ],
}

_PLATFORM_NEGATIVES = {
    "midjourney_v8_1": (
        "blurry, low quality, distorted, watermark, text overlay, "
        "oversaturated, bad anatomy, cropped, out of frame"
    ),
    "dalle_3": "",
    "nano_banana": "low quality, blurry, watermark, text overlay",
}

VALID_PLATFORMS = set(_PLATFORM_ENHANCERS.keys())


def compile_mj81(input_text: str, params: dict) -> dict:
    base = input_text.strip()
    if not base:
        return {"status": "EMPTY_INPUT", "message": "input_text is required"}

    platform = params.get("platform", "midjourney_v8_1")
    if platform not in VALID_PLATFORMS:
        platform = "midjourney_v8_1"

    enhancers = _PLATFORM_ENHANCERS[platform]

    if platform == "midjourney_v8_1":
        suffix = (
            f"--ar {params.get('ar', '1:1')} "
            f"--s {params.get('s', 100)} "
            f"--c {params.get('c', 0)} "
            f"--w {params.get('w', 0)} "
            f"--q {params.get('q', 1)} "
            "--v 8.1"
        )
        positive = f"{base}, {', '.join(enhancers)} {suffix}"
    else:
        positive = f"{base}, {', '.join(enhancers)}"

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
