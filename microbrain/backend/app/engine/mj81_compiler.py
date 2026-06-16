import os
import uuid

from app.engine.artifact_exporter import OUTPUTS_DIR

_ENHANCERS = [
    "cinematic composition",
    "high visual clarity",
    "detailed subject",
    "dramatic lighting",
    "rich atmosphere",
    "professional render",
]

_DEFAULT_NEGATIVE = (
    "blurry, low quality, distorted, watermark, text overlay, "
    "oversaturated, bad anatomy, cropped, out of frame"
)


def compile_mj81(input_text: str, params: dict) -> dict:
    base = input_text.strip()
    if not base:
        return {"status": "EMPTY_INPUT", "message": "input_text is required"}

    suffix = (
        f"--ar {params.get('ar', '1:1')} "
        f"--s {params.get('s', 100)} "
        f"--c {params.get('c', 0)} "
        f"--w {params.get('w', 0)} "
        f"--q {params.get('q', 1)} "
        "--v 8.1"
    )

    positive = f"{base}, {', '.join(_ENHANCERS)} {suffix}"

    output_mode = params.get("output_mode", "prompt_plus_negative")
    negative = _DEFAULT_NEGATIVE if output_mode == "prompt_plus_negative" else ""

    canvas = _render_canvas(positive, negative)
    file_meta = _save_txt(positive, negative)

    return {
        "status": "DONE_WITH_PROMPT",
        "positive_prompt": positive,
        "negative_prompt": negative,
        "canvas": canvas,
        "file": file_meta,
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
