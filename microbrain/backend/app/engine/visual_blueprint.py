import re

from app.engine.kimify_domains import infer_domain

# === Resemblance patterns (must run before character normalization) ===

_RESEMBLANCE_PATTERNS = [
    (r"con\s+(?:la\s+)?cara\s+de\s+([^,\.]+)", r"resembling \1"),
    (r"con\s+(?:el\s+)?rostro\s+de\s+([^,\.]+)", r"resembling \1"),
    (r"parecida?\s+a\s+([^,\.]+)", r"resembling \1"),
    (r"que\s+se\s+parece\s+a\s+([^,\.]+)", r"resembling \1"),
    (r"al\s+estilo\s+de\s+([^,\.]+)", r"in the style of \1"),
]

# Posture participle + preposition phrases, collapsed so the preposition
# doesn't get translated again right after (e.g. "apoyada en X" -> "leaning
# against X", not "leaning against in X").
_POSTURE_PATTERNS = [
    (r"apoyad[ao]\s+(?:en|contra)\s+", "leaning against "),
    (r"recostad[ao]\s+(?:en|sobre)\s+", "reclining on "),
    (r"sentad[ao]\s+(?:en|sobre)\s+", "seated on "),
    (r"parad[ao]\s+(?:en|sobre)\s+", "standing on "),
    (r"acostad[ao]\s+(?:en|sobre)\s+", "lying on "),
    (r"arrodillad[ao]\s+(?:en|sobre)\s+", "kneeling on "),
]

# === Translation tables ===

_ES_GERUNDS = {
    "levitando": "levitating", "volando": "flying", "corriendo": "running",
    "luchando": "fighting", "cayendo": "falling", "saltando": "jumping",
    "mirando": "looking", "sosteniendo": "holding", "caminando": "walking",
    "flotando": "floating", "destruyendo": "destroying", "atacando": "attacking",
    "defendiendo": "defending", "huyendo": "fleeing", "escalando": "climbing",
    "nadando": "swimming", "bailando": "dancing", "meditando": "meditating",
    "observando": "observing", "disparando": "shooting",
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
    "pared": "wall", "muro": "wall", "capa": "cape", "torre": "tower",
    "roca": "rock", "puerta": "door", "ventana": "window", "columna": "column",
    "estilo": "style",
}

_ES_ADJECTIVES = {
    "destruida": "destroyed", "destruido": "destroyed",
    "abandonada": "abandoned", "abandonado": "abandoned",
    "oscuro": "dark", "oscura": "dark",
    "luminoso": "bright", "luminosa": "bright",
    "apocalíptico": "apocalyptic", "épico": "epic",
    "mágico": "magical", "mágica": "magical",
    "antiguo": "ancient", "antigua": "ancient",
    "futurista": "futuristic", "helado": "frozen", "helada": "frozen",
    "ardiente": "burning", "sumergido": "submerged", "sumergida": "submerged",
    "nevado": "snowy", "nevada": "snowy", "lluvioso": "rainy", "lluviosa": "rainy",
    # Descriptor adjectives (critical for preserving user input)
    "sexy": "sexy", "sensual": "sensual",
    "muscular": "muscular", "musculosa": "muscular", "musculoso": "muscular",
    "definida": "defined", "definido": "defined",
    "alta": "tall", "alto": "tall",
    "baja": "short", "bajo": "short",
    "delgada": "slender", "delgado": "slender",
    "fuerte": "strong",
    "poderosa": "powerful", "poderoso": "powerful",
    "hermosa": "beautiful", "hermoso": "beautiful",
    "elegante": "elegant",
    "feroz": "fierce",
    "majestuosa": "majestic", "majestuoso": "majestic",
    "enorme": "enormous",
    "pequeña": "small", "pequeño": "small",
    "joven": "young",
    "anciana": "elderly", "anciano": "elderly",
    "veloce": "swift", "veloz": "swift",
    "brillante": "brilliant",
    "oscuro": "dark", "oscura": "dark",
    "luminosa": "radiant", "luminoso": "radiant",
    "dorada": "golden", "dorado": "golden",
    "plateada": "silver", "plateado": "silver",
    # Past-participle posture descriptors
    "apoyada": "leaning against", "apoyado": "leaning against",
    "recostada": "reclining", "recostado": "reclining",
    "sentada": "seated", "sentado": "seated",
    "parada": "standing", "parado": "standing",
    "acostada": "lying down", "acostado": "lying down",
    "arrodillada": "kneeling", "arrodillado": "kneeling",
    "hiper": "hyper",
}

_ES_PREPOSITIONS = {
    "sobre": "above", "encima": "above",
    "bajo": "below", "debajo": "below",
    "dentro": "inside",
    "fuera": "outside",
    "en": "in",
    "entre": "between",
    "detrás": "behind",
    "junto": "beside",
    "con": "with",
    "de": "of",
    "frente": "in front of",
}

_ARTICLES = {
    "un", "una", "el", "la", "los", "las", "unos", "unas",
    "al", "del",
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

# === Core functions ===

def translate_full_text(text: str) -> str:
    """Translate Spanish free text to English while preserving ALL descriptors and proper nouns."""
    result = text.strip().rstrip(",")

    # Step 1: Resemblance phrases (before any other substitution)
    for pattern, repl in _RESEMBLANCE_PATTERNS:
        result = re.sub(pattern, repl, result, flags=re.IGNORECASE)

    # Step 1b: Posture participle + preposition phrases (collapse before
    # the lone preposition gets translated again right after)
    for pattern, repl in _POSTURE_PATTERNS:
        result = re.sub(pattern, repl, result, flags=re.IGNORECASE)

    # Step 2: Normalize known character names (longest match first)
    for name in sorted(_CHARACTER_MAP, key=len, reverse=True):
        result = re.sub(rf"\b{re.escape(name)}\b", _CHARACTER_MAP[name], result, flags=re.IGNORECASE)

    # Step 3: Handle Spanish noun+adj → English adj+noun word order
    for es_noun, en_noun in _ES_NOUNS.items():
        for es_adj, en_adj in _ES_ADJECTIVES.items():
            result = re.sub(
                rf"\b{re.escape(es_noun)}\s+{re.escape(es_adj)}\b",
                f"{en_adj} {en_noun}", result, flags=re.IGNORECASE,
            )

    # Step 4: Token-by-token translation of remaining Spanish words
    tokens = result.split()
    translated = []
    for token in tokens:
        match = re.match(r"^([.,;]*)(.*?)([.,;]*)$", token)
        prefix_punct, clean, suffix_punct = match.groups()
        t = clean.lower()

        if t in _ARTICLES:
            continue  # Drop Spanish articles

        en = (
            _ES_GERUNDS.get(t)
            or _ES_PREPOSITIONS.get(t)
            or _ES_NOUNS.get(t)
            or _ES_ADJECTIVES.get(t)
            or clean  # Keep as-is: English words, proper nouns, already-translated text
        )
        translated.append(prefix_punct + en + suffix_punct)

    return " ".join(translated)


def parse_blueprint(text: str) -> dict:
    """Parse free text into a full KIMIFY-layered blueprint.

    The kernel description is translated Spanish->English (translate_full_text),
    while every other layer (Intent/Medium/Illumination/Format/Yield) is resolved
    by the shared domain-detection engine (kimify_domains.infer_domain), the same
    one that powers the Pro Builder's auto-inference, so every platform compiler
    applies the same prompt-engineering rules instead of single-value heuristics.
    """
    # Strip MJ suffix flags before parsing
    clean = re.sub(r"--\w+\s*\S*", "", text).strip()

    full_description = translate_full_text(clean)
    domain_result = infer_domain(clean)
    fields = domain_result["fields"]

    return {
        "full_description": full_description,
        "subject_details": fields["subject_details"],
        "subject_modifiers": fields["subject_modifiers"],
        "style_intent": fields["style_intent"],
        "mood": fields["mood"],
        "visual_style": fields["visual_style"],
        "era_period": fields["era_period"],
        "camera": fields["camera"],
        "lens": fields["lens"],
        "film": fields["film"],
        "rendering_engine": fields["rendering_engine"],
        "lighting": fields["lighting"],
        "time_of_day": fields["time_of_day"],
        "atmosphere": fields["atmosphere"],
        "weather": fields["weather"],
        "composition": fields["composition"],
        "angle": fields["angle"],
        "dof": fields["dof"],
        "color": fields["color"],
        "aspect_ratio": fields["aspect_ratio"],
        "stylize": fields["stylize"],
        "chaos": fields["chaos"],
        "raw": fields["raw"],
        "negative": fields["negative"],
        "domain_id": domain_result["meta"]["domain_id"],
        "domain_label": domain_result["meta"]["label"],
        "matched_keywords": domain_result["meta"]["matched_keywords"],
    }
