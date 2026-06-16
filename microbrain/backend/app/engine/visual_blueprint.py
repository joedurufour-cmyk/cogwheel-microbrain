import re

# === Spanish → English translation tables ===

_ES_GERUNDS = {
    "levitando": "levitating", "volando": "flying", "corriendo": "running",
    "luchando": "fighting", "cayendo": "falling", "saltando": "jumping",
    "mirando": "looking", "sosteniendo": "holding", "caminando": "walking",
    "flotando": "floating", "destruyendo": "destroying", "atacando": "attacking",
    "defendiendo": "defending", "huyendo": "fleeing", "escalando": "climbing",
    "nadando": "swimming", "bailando": "dancing", "meditando": "meditating",
    "observando": "observing", "disparando": "shooting", "corriendo": "running",
}

_ES_NOUNS = {
    "ciudad": "city", "bosque": "forest", "desierto": "desert",
    "montaña": "mountain", "océano": "ocean", "mar": "sea", "cielo": "sky",
    "noche": "night", "amanecer": "dawn", "atardecer": "sunset",
    "fuego": "fire", "agua": "water", "hielo": "ice", "nieve": "snow",
    "lluvia": "rain", "tormenta": "storm", "nebulosa": "nebula",
    "espacio": "space", "galaxia": "galaxy", "universo": "universe",
    "puente": "bridge", "rascacielo": "skyscraper", "templo": "temple",
    "castillo": "castle", "ruinas": "ruins", "selva": "jungle",
    "cueva": "cave", "aldea": "village", "metrópoli": "metropolis",
    "laboratorio": "laboratory", "nave": "spaceship", "planeta": "planet",
    "arena": "sand", "playa": "beach", "isla": "island", "volcán": "volcano",
    "techo": "rooftop", "calle": "street", "edificio": "building",
}

_ES_ADJECTIVES = {
    "destruida": "destroyed", "destruido": "destroyed",
    "abandonada": "abandoned", "abandonado": "abandoned",
    "oscuro": "dark", "oscura": "dark", "luminoso": "bright", "luminosa": "bright",
    "apocalíptico": "apocalyptic", "épico": "epic", "mágico": "magical",
    "antiguo": "ancient", "antigua": "ancient", "futurista": "futuristic",
    "helado": "frozen", "helada": "frozen", "ardiente": "burning",
    "sumergido": "submerged", "sumergida": "submerged",
    "nebuloso": "misty", "nevado": "snowy", "lluvioso": "rainy",
    "cyberpunk": "cyberpunk", "neon": "neon-lit",
}

_ARTICLES = {
    "un", "una", "el", "la", "los", "las", "unos", "unas",
    "de", "del", "al", "en", "con", "y", "a", "the", "an", "a",
}

_CHARACTER_MAP = {
    "supergirl": "superheroine", "superman": "superhero",
    "batman": "dark knight", "batgirl": "dark heroine",
    "wonder woman": "warrior goddess", "iron man": "armored hero",
    "spider-man": "web-slinging hero", "spiderman": "web-slinging hero",
    "thor": "norse god warrior", "hulk": "hulking green warrior",
    "captain america": "super soldier", "black widow": "elite spy",
    "aquaman": "underwater king", "flash": "speedster hero",
    "green lantern": "cosmic guardian", "catwoman": "feline thief",
    "guerrero": "warrior", "guerrera": "female warrior",
    "mago": "sorcerer", "maga": "sorceress",
    "bruja": "witch", "brujo": "warlock",
    "dragón": "dragon", "dragon": "dragon",
    "robot": "robot", "androide": "android", "cyborg": "cyborg",
    "astronauta": "astronaut", "vikingo": "viking warrior",
    "samurai": "samurai", "ninja": "ninja",
    "caballero": "knight", "princesa": "princess",
    "reina": "queen", "rey": "king",
    "soldado": "soldier", "detective": "detective",
    "héroe": "hero", "heroína": "heroine",
    "villano": "villain", "villana": "villainess",
    "científico": "scientist", "explorador": "explorer",
}

# === Inference rule tables ===

_MOOD_RULES = [
    (["destruida", "destruido", "destroyed", "ruinas", "ruins", "apocalíptico",
      "apocalyptic", "caos", "chaos", "post-apocalíptico"], "epic"),
    (["tormenta", "storm", "oscuro", "dark", "horror", "sombra", "shadow",
      "miedo", "nightmare", "terror"], "ominous"),
    (["magia", "magic", "mágico", "magical", "fantasía", "fantasy",
      "hada", "fairy", "encantado", "enchanted"], "mystical"),
    (["amor", "love", "romance", "tierno", "tender"], "romantic"),
    (["batalla", "battle", "guerra", "war", "lucha", "fight",
      "combate", "combat", "atacando", "attack"], "intense"),
    (["paz", "peace", "sereno", "serene", "calma", "calm",
      "bosque", "forest"], "serene"),
    (["espacio", "space", "galaxia", "galaxy", "cosmos",
      "nebulosa", "nebula", "stars"], "cosmic"),
    (["cyberpunk", "neon", "futuro", "future", "cyber",
      "digital", "holographic", "futurista"], "futuristic"),
    (["llamas", "flames", "fuego", "fire", "ardiente", "burning",
      "volcán", "volcano"], "intense"),
]

_LIGHTING_RULES = [
    (["noche", "night", "luna", "moon", "moonlit"], "moonlit"),
    (["amanecer", "dawn", "sunrise"], "golden hour"),
    (["atardecer", "sunset", "crepúsculo", "dusk"], "golden hour"),
    (["fuego", "fire", "llamas", "flames", "ardiente", "burning"], "firelit"),
    (["tormenta", "storm", "relámpago", "lightning"], "stormy backlight"),
    (["espacio", "space", "galaxia", "galaxy", "nebulosa", "nebula"], "cosmic glow"),
    (["neon", "cyberpunk", "holographic", "futurista"], "neon lit"),
    (["sol", "sun", "soleado", "sunny", "día claro", "daylight"], "natural daylight"),
]

_CAMERA_RULES = [
    (["levitando", "levitating", "volando", "flying",
      "flotando", "floating", "sobre el", "above"], "low angle wide shot"),
    (["ciudad", "city", "paisaje", "landscape",
      "espacio", "space", "galaxia", "galaxy", "metrópoli"], "wide shot"),
    (["retrato", "portrait", "cara", "face", "rostro", "close up", "close-up"], "close-up portrait"),
    (["batalla", "battle", "atacando", "fighting", "acción", "action"], "dynamic action shot"),
    (["cayendo", "falling", "desde arriba", "overhead"], "bird's eye view"),
]

_STYLE_RULES = [
    (["cyberpunk", "neon", "cyber", "holographic", "futurista"], "cyberpunk aesthetic"),
    (["anime", "manga", "shonen", "shojo"], "anime style"),
    (["fantasía", "fantasy", "dragón", "dragon", "magia", "magic",
      "castillo", "castle", "hada", "fairy"], "fantasy concept art"),
    (["espacio", "space", "galaxia", "galaxy", "nebulosa", "nebula",
      "sci-fi", "ciencia ficción", "nave espacial"], "science fiction concept art"),
    (["foto", "photo", "real", "realista", "realistic", "fotografía"], "photorealistic"),
    (["pintura", "painting", "óleo", "oil"], "oil painting"),
    (["acuarela", "watercolor", "watercolour"], "watercolor painting"),
    (["pixel", "retro", "8bit", "8-bit"], "pixel art"),
]


# === Core parsing functions ===

def _match_rule(text: str, rules: list) -> str | None:
    for keywords, value in rules:
        if any(k in text for k in keywords):
            return value
    return None


def _translate_phrase(text: str) -> str:
    """Translate a Spanish phrase to English, handling noun+adj → adj+noun order."""
    tokens = re.split(r"[\s,]+", text.lower())
    result = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if not t or t in _ARTICLES:
            i += 1
            continue
        noun_en = _ES_NOUNS.get(t)
        if noun_en and i + 1 < len(tokens):
            next_t = tokens[i + 1]
            if next_t not in _ARTICLES:
                adj_en = _ES_ADJECTIVES.get(next_t)
                if adj_en:
                    result.append(f"{adj_en} {noun_en}")
                    i += 2
                    continue
        en = (
            _ES_GERUNDS.get(t) or _ES_NOUNS.get(t) or
            _ES_ADJECTIVES.get(t) or (None if t in _ARTICLES else t)
        )
        if en:
            result.append(en)
        i += 1
    return " ".join(result).strip()


def _extract_subject(text: str) -> str:
    text_lower = text.lower()
    for name in sorted(_CHARACTER_MAP, key=len, reverse=True):
        if name in text_lower:
            return _CHARACTER_MAP[name]
    tokens = re.split(r"[\s,]+", text)
    for token in tokens:
        t = token.lower()
        if t in _ARTICLES or t in _ES_GERUNDS:
            continue
        if t in _ES_NOUNS:
            return _ES_NOUNS[t]
        if t.istitle() or t.isupper():
            return token
        if not re.match(r"^-", t):
            return token.capitalize()
    return "figure"


def _extract_action(text: str) -> str:
    text_lower = text.lower()
    for es, en in _ES_GERUNDS.items():
        if es in text_lower:
            return en
    for en_g in ["levitating", "flying", "running", "fighting", "falling",
                 "jumping", "walking", "floating", "attacking", "watching"]:
        if en_g in text_lower:
            return en_g
    return ""


def _extract_environment(text: str) -> str:
    text_lower = text.lower()
    # Strip MJ flags from search space
    clean = re.sub(r"--\w+\s*\S*", "", text_lower).strip()

    prep_patterns = [
        r"(?:sobre|encima de)\s+(?:una?\s+)?(.+)",
        r"(?:en|dentro de)\s+(?:una?\s+)?(.+)",
        r"(?:above|on top of)\s+(?:an?\s+)?(.+)",
        r"(?:in|inside)\s+(?:an?\s+)?(.+)",
    ]
    for pat in prep_patterns:
        m = re.search(pat, clean)
        if m:
            raw = m.group(1).strip()
            translated = _translate_phrase(raw)
            if translated:
                return translated

    # Fallback: look for known environment nouns
    for es, en in sorted(_ES_NOUNS.items(), key=lambda x: len(x[0]), reverse=True):
        if es in clean:
            # Check for adjacent adjective
            adj_match = re.search(rf"{re.escape(es)}\s+(\w+)", clean)
            if adj_match:
                adj = adj_match.group(1)
                adj_en = _ES_ADJECTIVES.get(adj, "")
                return f"{adj_en} {en}".strip() if adj_en else en
            return en

    return ""


def parse_blueprint(text: str) -> dict:
    """Parse free text into a VisualBlueprint dict."""
    clean = re.sub(r"--\w+\s*\S*", "", text).strip()
    text_lower = clean.lower()

    return {
        "subject": _extract_subject(clean),
        "action": _extract_action(clean),
        "environment": _extract_environment(clean),
        "style": _match_rule(text_lower, _STYLE_RULES) or "cinematic realism",
        "mood": _match_rule(text_lower, _MOOD_RULES) or "epic",
        "lighting": _match_rule(text_lower, _LIGHTING_RULES) or "dramatic",
        "camera": _match_rule(text_lower, _CAMERA_RULES) or "wide shot",
        "quality": "high detail",
    }
