import os
import re
import uuid

VALID_OUTPUTS: dict[str, str] = {
    "app_stack": "md",
    "python_code": "py",
    "advanced_prompt": "txt",
    "text": "md",
    "csv": "csv",
}

OUTPUTS_DIR = os.getenv("OUTPUTS_DIR", "outputs/generated")


def compile_and_export(output_type: str, compiled_deliverable: dict) -> dict:
    if not output_type or output_type not in VALID_OUTPUTS:
        return {
            "status": "BLOCKED_MISSING_OUTPUT_TYPE",
            "message": "Elige: app_stack, python_code, advanced_prompt, text, csv",
        }
    content = _extract_content_string(compiled_deliverable, output_type)
    if not content:
        return {"status": "ERROR_NO_COMPILER", "output_type": output_type}
    file_meta = _save_artifact(content, output_type)
    return {
        "status": "DONE_WITH_ARTIFACT",
        "output_type": output_type,
        "canvas": content,
        "file": file_meta,
    }


def _extract_content_string(compiled: dict, output_type: str) -> str:
    preview = compiled.get("compiled_preview") or ""
    if output_type == "python_code":
        m = re.search(r"```python\n(.*?)```", preview, re.DOTALL)
        return m.group(1).strip() if m else preview
    if output_type == "csv":
        m = re.search(r"```csv\n(.*?)```", preview, re.DOTALL)
        return m.group(1).strip() if m else preview
    if output_type == "advanced_prompt":
        pos = compiled.get("positive_prompt") or ""
        params = compiled.get("parameters") or ""
        return f"{pos} {params}".strip() if pos else preview
    # app_stack and text: preview is already clean markdown
    return preview


def _save_artifact(content: str, output_type: str) -> dict:
    ext = VALID_OUTPUTS[output_type]
    filename = f"artifact_{uuid.uuid4().hex[:8]}.{ext}"
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    path = os.path.join(OUTPUTS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return {
        "filename": filename,
        "path": path,
        "download_url": f"/outputs/{filename}",
    }
