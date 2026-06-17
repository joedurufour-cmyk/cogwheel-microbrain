"""Fixed output-style presets.

Unlike kimify_domains.DOMAINS (which infers *scene* fields like mood,
composition, angle from the free text), these presets describe a fixed
*rendering medium/look* that's applied on top of the inferred domain,
independent of what the scene is about. Used to compile the same Kernel
into all 6 styles at once via compile_all_styles() below, without
touching infer_domain/translate_full_text or the existing single-style
compile path.
"""

STYLE_PRESETS = [
    {
        "id": "cinema",
        "label": "Cine / Cinematográfico",
        "visual_style": "cinematic, movie still, anamorphic lens flare, film grain",
        "style_intent": "cinematic movie still, blockbuster film photography",
        "camera": "shot on ARRI Alexa 65",
        "lens": "anamorphic 40mm lens, subtle lens flare",
        "film": "Kodak Vision3 500T film stock",
        "rendering_engine": "",
        "color": "teal and orange cinematic LUT, color graded",
        "lighting": "motivated practical lighting, volumetric haze",
        "aspect_ratio": "21:9", "stylize": 350, "chaos": 20, "raw": False,
    },
    {
        "id": "vintage_photo",
        "label": "Foto vintage",
        "visual_style": "vintage analog photography, retro film aesthetic, nostalgic",
        "style_intent": "vintage film photography, 1970s analog look",
        "camera": "shot on Leica M6 rangefinder",
        "lens": "50mm f/1.4 vintage lens, soft vignette",
        "film": "Kodak Portra 400 film, grain texture, light leaks",
        "rendering_engine": "",
        "color": "faded warm tones, sepia undertone, desaturated highlights",
        "lighting": "soft natural window light, warm afternoon glow",
        "aspect_ratio": "4:5", "stylize": 150, "chaos": 10, "raw": True,
    },
    {
        "id": "anime_dark_pro",
        "label": "Anime Dark Pro",
        "visual_style": "dark fantasy anime, Anime Dark Pro style, high-contrast cel shading",
        "style_intent": "professional anime illustration, dark fantasy manga aesthetic",
        "camera": "", "lens": "", "film": "",
        "rendering_engine": "anime production cel-shading pipeline, digital ink and paint",
        "color": "deep shadows, saturated neon accents, high contrast palette",
        "lighting": "dramatic rim lighting, dark moody atmosphere",
        "aspect_ratio": "2:3", "stylize": 600, "chaos": 30, "raw": False,
    },
    {
        "id": "ghibli",
        "label": "Studio Ghibli",
        "visual_style": "Studio Ghibli style, hand-painted anime, whimsical watercolor backgrounds",
        "style_intent": "Hayao Miyazaki inspired animation still, soft painterly illustration",
        "camera": "", "lens": "", "film": "",
        "rendering_engine": "traditional 2D cel animation, watercolor background art",
        "color": "soft pastel palette, warm natural tones",
        "lighting": "soft diffused daylight, gentle volumetric light through leaves",
        "aspect_ratio": "16:9", "stylize": 250, "chaos": 15, "raw": False,
    },
    {
        "id": "pvc_resin_3d",
        "label": "PVC Resina 3D Realista",
        "visual_style": "PVC resin figure, collectible action figure render, realistic toy photography",
        "style_intent": "commercial product photography of a 1/7 scale PVC resin figure",
        "camera": "", "lens": "", "film": "",
        "rendering_engine": "ZBrush sculpt, Substance Painter PBR textures, Octane Render",
        "color": "studio-accurate color calibration, glossy resin highlights",
        "lighting": "softbox studio lighting, three-point setup, subtle specular highlights",
        "dof": "shallow depth of field, product on display base, blurred shelf background",
        "aspect_ratio": "1:1", "stylize": 100, "chaos": 0, "raw": True,
    },
    {
        "id": "cgi_3d_realistic",
        "label": "CGI 3D Realista",
        "visual_style": "full CGI render, photorealistic 3D, hyperrealistic digital rendering",
        "style_intent": "high-end CGI rendering, AAA game cinematic quality",
        "camera": "", "lens": "", "film": "",
        "rendering_engine": "Unreal Engine 5, Lumen global illumination, Nanite geometry",
        "color": "physically accurate PBR materials, realistic color grading",
        "lighting": "ray-traced global illumination, HDRI environment lighting",
        "dof": "cinematic depth of field, ray-traced reflections",
        "aspect_ratio": "16:9", "stylize": 400, "chaos": 15, "raw": False,
    },
]


def apply_style_preset(blueprint: dict, preset: dict) -> dict:
    """Overlay a style preset's medium/look fields onto an inferred blueprint.

    Scene-level fields (mood, atmosphere, composition, angle, era_period,
    time_of_day, weather, subject_*) are left untouched since they describe
    what's happening, not how it's rendered.
    """
    overridable = (
        "visual_style", "style_intent", "camera", "lens", "film",
        "rendering_engine", "color", "lighting", "dof",
        "aspect_ratio", "stylize", "chaos", "raw",
    )
    overlaid = dict(blueprint)
    for key in overridable:
        if key in preset:
            overlaid[key] = preset[key]
    return overlaid
