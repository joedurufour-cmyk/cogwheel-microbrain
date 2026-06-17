from app.engine.mj81_compiler import compile_mj81_all_styles
from app.engine.style_presets import STYLE_PRESETS


def test_compile_all_styles_returns_six_variants():
    result = compile_mj81_all_styles("Supergirl en una ciudad cyberpunk de noche", {"platform": "midjourney_v8_1"})
    assert result["status"] == "DONE_WITH_VARIANTS"
    assert len(result["variants"]) == len(STYLE_PRESETS) == 6
    style_ids = {v["style_id"] for v in result["variants"]}
    assert style_ids == {p["id"] for p in STYLE_PRESETS}


def test_compile_all_styles_keeps_scene_inference_and_applies_preset_overrides():
    result = compile_mj81_all_styles("Supergirl en una ciudad cyberpunk de noche", {"platform": "midjourney_v8_1"})
    cinema = next(v for v in result["variants"] if v["style_id"] == "cinema")
    ghibli = next(v for v in result["variants"] if v["style_id"] == "ghibli")
    # Scene-level inference (translated kernel, cyberpunk mood) present in every variant
    assert "superheroine" in cinema["positive_prompt"]
    assert "mysterious, enigmatic atmosphere" in cinema["positive_prompt"]
    assert "mysterious, enigmatic atmosphere" in ghibli["positive_prompt"]
    # Preset-specific medium/look differs per variant
    assert "ARRI Alexa 65" in cinema["positive_prompt"]
    assert "Studio Ghibli" in ghibli["positive_prompt"]
    assert "--ar 21:9" in cinema["positive_prompt"]
    assert "--ar 16:9" in ghibli["positive_prompt"]


def test_compile_all_styles_empty_input():
    result = compile_mj81_all_styles("   ", {})
    assert result["status"] == "EMPTY_INPUT"
