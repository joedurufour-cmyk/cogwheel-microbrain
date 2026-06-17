"""KIMIFY domain-detection + 6-layer inference engine.

Python mirror of the frontend's kimifyInference.js: classifies free text
into a visual "domain" via keyword scoring, then resolves the domain to
concrete KIMIFY layer values (Intent / Medium / Illumination / Format /
Yield), so every platform compiler shares the same prompt-engineering
rules as the Pro Builder UI instead of reinventing single-value heuristics.
"""

import re

DOMAINS = [
    {
        "id": "superhero_action",
        "label": "Acción heroica / superhéroe",
        "keywords": ["supergirl", "superman", "superhero", "super hero", "heroina", "heroína", "heroe", "héroe",
                     "batman", "wonder woman", "muscular", "warrior", "guerrera", "guerrero", "tactical", "cape",
                     "capa", "powerful", "poderosa", "action pose"],
        "mood": "epic, grandiose scale",
        "visual_style": "cinematic, movie still, film grain",
        "camera": "shot on Canon EOS R5 / Nikon Z9",
        "lens": "35mm f/1.4 lens, classic photojournalism",
        "lighting": "strong rim lighting, backlight silhouette, edge glow",
        "composition": "leading lines drawing eye to subject",
        "angle": "low angle shot, looking up, heroic perspective",
        "dof": "moderate depth of field, f/4, subject sharp, background soft",
        "color": "warm color grading, teal and orange cinematic LUT",
        "style_intent": "cinematic superhero photography, movie poster style",
        "aspect_ratio": "2:3", "stylize": 350, "chaos": 20, "raw": False,
        "subject_details": ["dynamic pose, mid-action", "hyper-detailed textures, visible pores and fibers"],
        "subject_modifiers": ["hyper-detailed", "photorealistic", "masterpiece"],
    },
    {
        "id": "fashion_editorial",
        "label": "Moda / editorial",
        "keywords": ["fashion", "moda", "editorial", "model", "modelo", "vogue", "runway", "pasarela", "outfit",
                     "vestimenta", "street style"],
        "mood": "dramatic, intense atmosphere",
        "visual_style": "editorial photography, magazine quality",
        "camera": "shot on Canon EOS R5 / Nikon Z9",
        "lens": "85mm f/1.2 portrait lens, creamy bokeh",
        "lighting": "three-point studio lighting, key/fill/rim setup",
        "composition": "rule of thirds composition",
        "angle": "three-quarter view, flattering portrait angle",
        "dof": "shallow depth of field, f/1.8, soft background blur",
        "color": "warm color grading, teal and orange cinematic LUT",
        "style_intent": "editorial fashion photography",
        "aspect_ratio": "3:4", "stylize": 300, "chaos": 30, "raw": False,
        "subject_modifiers": ["photorealistic", "professional"],
    },
    {
        "id": "portrait",
        "label": "Retrato",
        "keywords": ["retrato", "portrait", "headshot", "rostro", "face close", "close-up face", "close up portrait"],
        "mood": "serene, peaceful atmosphere",
        "visual_style": "photorealistic, indistinguishable from photograph",
        "camera": "shot on Canon EOS R5 / Nikon Z9",
        "lens": "85mm f/1.2 portrait lens, creamy bokeh",
        "lighting": "Rembrandt lighting, triangular highlight on cheek",
        "composition": "rule of thirds composition",
        "angle": "eye-level shot, neutral perspective",
        "dof": "extremely shallow depth of field, f/1.2, creamy bokeh",
        "color": "warm color grading, teal and orange cinematic LUT",
        "style_intent": "editorial portrait photography",
        "aspect_ratio": "4:5", "stylize": 150, "chaos": 5, "raw": True,
    },
    {
        "id": "cyberpunk",
        "label": "Cyberpunk / sci-fi urbano",
        "keywords": ["cyberpunk", "neon", "futuristic", "futurista", "dystopia", "distopia", "blade runner", "cyber"],
        "mood": "mysterious, enigmatic atmosphere",
        "visual_style": "cyberpunk, neon-lit, futuristic dystopia",
        "lighting": "neon lighting, magenta and cyan rim lights",
        "atmosphere": "thin smoke, atmospheric depth, moody haze",
        "composition": "leading lines drawing eye to subject",
        "angle": "low angle shot, looking up, heroic perspective",
        "dof": "moderate depth of field, f/4, subject sharp, background soft",
        "color": "neon color grading, magenta cyan highlights",
        "style_intent": "cyberpunk concept photography",
        "aspect_ratio": "16:9", "stylize": 500, "chaos": 40, "raw": False,
    },
    {
        "id": "product_commercial",
        "label": "Producto comercial",
        "keywords": ["producto", "product", "ecommerce", "watch", "reloj", "bottle", "botella", "perfume", "packshot"],
        "visual_style": "photorealistic, indistinguishable from photograph",
        "lighting": "three-point studio lighting, key/fill/rim setup",
        "composition": "centered symmetrical composition",
        "angle": "eye-level shot, neutral perspective",
        "dof": "deep depth of field, f/11, everything in focus",
        "color": "highly saturated, vibrant punchy colors",
        "style_intent": "commercial product photography",
        "aspect_ratio": "1:1", "stylize": 50, "chaos": 0, "raw": True,
    },
    {
        "id": "landscape_nature",
        "label": "Paisaje / naturaleza",
        "keywords": ["paisaje", "landscape", "mountain", "montaña", "forest", "bosque", "ocean", "océano", "valley",
                     "valle", "nature", "naturaleza", "vista"],
        "mood": "epic, grandiose scale",
        "visual_style": "fine art photography, gallery quality",
        "lighting": "golden hour lighting, warm 3200K, long shadows",
        "atmosphere": "vivid sunset, golden light, dramatic sky colors",
        "composition": "wide angle, expansive field of view, environmental",
        "angle": "high angle shot, looking down, dominant perspective",
        "dof": "deep depth of field, f/11, everything in focus",
        "color": "earthy tones, muted greens and browns, natural palette",
        "style_intent": "epic landscape photography",
        "aspect_ratio": "16:9", "stylize": 350, "chaos": 15, "raw": False,
    },
    {
        "id": "wildlife_macro",
        "label": "Vida salvaje / macro",
        "keywords": ["macro", "insect", "insecto", "wildlife", "vida salvaje", "butterfly", "mariposa", "animal close"],
        "visual_style": "photorealistic, indistinguishable from photograph",
        "lighting": "harsh midday sun, high contrast, sharp shadows",
        "composition": "extreme macro, detail-focused, shallow DoF",
        "angle": "eye-level shot, neutral perspective",
        "dof": "extremely shallow depth of field, f/1.2, creamy bokeh",
        "color": "highly saturated, vibrant punchy colors",
        "style_intent": "macro wildlife photography",
        "aspect_ratio": "3:2", "stylize": 80, "chaos": 10, "raw": True,
    },
    {
        "id": "horror_gothic",
        "label": "Horror / gótico",
        "keywords": ["horror", "terror", "gothic", "gótico", "mansion", "haunted", "embrujada", "siniestro",
                     "sombrio", "sombrío"],
        "mood": "somber, grave atmosphere",
        "visual_style": "Baroque, dramatic chiaroscuro, ornate details",
        "lighting": "strong rim lighting, backlight silhouette, edge glow",
        "atmosphere": "dense fog, atmospheric haze, muted visibility",
        "composition": "natural framing, subject framed by environment",
        "angle": "low angle shot, looking up, heroic perspective",
        "dof": "moderate depth of field, f/4, subject sharp, background soft",
        "color": "desaturated, muted tones, low saturation",
        "style_intent": "gothic horror cinematic photography",
        "aspect_ratio": "21:9", "stylize": 380, "chaos": 30, "raw": False,
    },
    {
        "id": "cinematic_film",
        "label": "Cinematográfico",
        "keywords": ["cinematic", "cinematográfico", "película", "movie still", "film noir", "western", "standoff"],
        "mood": "tense, suspenseful mood",
        "visual_style": "cinematic, movie still, film grain",
        "lighting": "strong rim lighting, backlight silhouette, edge glow",
        "composition": "leading lines drawing eye to subject",
        "angle": "low angle shot, looking up, heroic perspective",
        "dof": "moderate depth of field, f/4, subject sharp, background soft",
        "color": "warm color grading, teal and orange cinematic LUT",
        "style_intent": "cinematic movie still",
        "aspect_ratio": "21:9", "stylize": 350, "chaos": 25, "raw": False,
    },
    {
        "id": "fine_art_bw",
        "label": "Bellas artes / blanco y negro",
        "keywords": ["black and white", "blanco y negro", "b&w", "monochrome", "fine art"],
        "mood": "melancholic, contemplative mood",
        "visual_style": "fine art photography, gallery quality",
        "lighting": "split lighting, half face lit, half in shadow",
        "composition": "negative space, minimalist composition",
        "angle": "eye-level shot, neutral perspective",
        "dof": "shallow depth of field, f/1.8, soft background blur",
        "color": "black and white, monochrome, tonal contrast",
        "style_intent": "fine art black and white photography",
        "aspect_ratio": "3:2", "stylize": 400, "chaos": 20, "raw": False,
    },
    {
        "id": "architecture_interior",
        "label": "Arquitectura / interiorismo",
        "keywords": ["arquitectura", "architecture", "interior", "interiorismo", "building", "edificio",
                     "habitación", "habitacion"],
        "visual_style": "minimalist, clean lines, negative space",
        "lighting": "soft overcast light, diffused, even illumination",
        "composition": "leading lines drawing eye to subject",
        "angle": "eye-level shot, neutral perspective",
        "dof": "deep depth of field, f/11, everything in focus",
        "color": "cool color palette, blue monochromatic grading",
        "style_intent": "architectural interior photography",
        "aspect_ratio": "16:9", "stylize": 150, "chaos": 5, "raw": True,
    },
    {
        "id": "fantasy_concept_art",
        "label": "Fantasía / concept art",
        "keywords": ["fantasy", "fantasía", "concept art", "dragon", "dragón", "magic", "mágico", "spaceship",
                     "nave espacial"],
        "mood": "epic, grandiose scale",
        "visual_style": "surreal, dreamlike, impossible geometry",
        "lighting": "volumetric lighting, god rays, light beams through haze",
        "composition": "layered composition, foreground midground background",
        "angle": "low angle shot, looking up, heroic perspective",
        "dof": "moderate depth of field, f/4, subject sharp, background soft",
        "color": "cool color palette, blue monochromatic grading",
        "style_intent": "fantasy concept art",
        "aspect_ratio": "16:9", "stylize": 500, "chaos": 30, "raw": False,
    },
]

DEFAULT_DOMAIN = {
    "id": "general_photoreal",
    "label": "General fotorrealista (sin dominio detectado)",
    "mood": "serene, peaceful atmosphere",
    "visual_style": "photorealistic, indistinguishable from photograph",
    "lighting": "golden hour lighting, warm 3200K, long shadows",
    "composition": "rule of thirds composition",
    "angle": "eye-level shot, neutral perspective",
    "dof": "shallow depth of field, f/1.8, soft background blur",
    "color": "warm color grading, teal and orange cinematic LUT",
    "style_intent": "professional photography",
    "aspect_ratio": "1:1", "stylize": 100, "chaos": 0, "raw": False,
}

_TIME_OF_DAY_RULES = [
    (re.compile(r"\bnight\b|\bnoche\b|nighttime"), "night, after dark"),
    (re.compile(r"\bdawn\b|\bamanecer\b|sunrise"), "dawn, early morning light"),
    (re.compile(r"\bdusk\b|\batardecer\b|twilight"), "dusk, twilight"),
    (re.compile(r"\bnoon\b|\bmediod[ií]a\b"), "midday"),
]

_WEATHER_RULES = [
    (re.compile(r"\brain\b|\blluvia\b"), "light rain, wet surfaces"),
    (re.compile(r"\bsnow\b|\bnieve\b"), "snowfall"),
    (re.compile(r"\bstorm\b|\btormenta\b"), "stormy weather"),
]

_ERA_RULES = [
    (re.compile(r"\b(19|20)\d0s\b"), None),
    (re.compile(r"medieval"), "medieval period"),
    (re.compile(r"futuristic|futurista"), "far future"),
]

_RENDER_ENGINE_RULES = [
    (re.compile(r"\b3d\b|render|cgi"), "Octane Render"),
    (re.compile(r"unreal"), "Unreal Engine 5"),
]

DEFAULT_NEGATIVE = "text, watermark, blurry, deformed, extra limbs, low quality"


def infer_domain(subject_text: str) -> dict:
    """Detect the best-matching visual domain and resolve it to full KIMIFY layer fields."""
    text = (subject_text or "").lower()

    domain = DEFAULT_DOMAIN
    matched_keywords: list[str] = []
    best_score = 0
    for candidate in DOMAINS:
        matched = [k for k in candidate["keywords"] if k in text]
        if len(matched) > best_score:
            best_score = len(matched)
            domain = candidate
            matched_keywords = matched

    fields = {
        "mood": domain.get("mood", ""),
        "visual_style": domain.get("visual_style", ""),
        "camera": domain.get("camera", ""),
        "lens": domain.get("lens", ""),
        "film": domain.get("film", ""),
        "rendering_engine": domain.get("rendering_engine", ""),
        "lighting": domain.get("lighting", ""),
        "atmosphere": domain.get("atmosphere", ""),
        "composition": domain.get("composition", ""),
        "angle": domain.get("angle", ""),
        "dof": domain.get("dof", ""),
        "color": domain.get("color", ""),
        "style_intent": domain.get("style_intent", ""),
        "aspect_ratio": domain.get("aspect_ratio", "1:1"),
        "stylize": domain.get("stylize", 100),
        "chaos": domain.get("chaos", 0),
        "raw": domain.get("raw", False),
        "subject_details": list(domain.get("subject_details", [])),
        "subject_modifiers": list(domain.get("subject_modifiers", [])),
        "era_period": "",
        "time_of_day": "",
        "weather": "",
    }

    for pattern, value in _TIME_OF_DAY_RULES:
        if pattern.search(text):
            fields["time_of_day"] = value
            break
    for pattern, value in _WEATHER_RULES:
        if pattern.search(text):
            fields["weather"] = value
            break
    for pattern, value in _ERA_RULES:
        match = pattern.search(text)
        if match:
            fields["era_period"] = value or match.group(0)
            break
    for pattern, value in _RENDER_ENGINE_RULES:
        if pattern.search(text):
            fields["rendering_engine"] = value
            break

    fields["negative"] = DEFAULT_NEGATIVE

    return {
        "fields": fields,
        "meta": {
            "domain_id": domain["id"],
            "label": domain["label"],
            "matched_keywords": matched_keywords,
        },
    }
