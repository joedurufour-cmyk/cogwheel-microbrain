"""Platform-specific prompt compilers.

Each compiler takes the full KIMIFY-layered blueprint dict produced by
visual_blueprint.parse_blueprint() and formats it for the target platform,
mirroring the layer assembly order used by the frontend's promptBuilder.js
(Kernel -> Intent -> Medium -> Illumination -> Format) so Midjourney, DALL-E
and Nano Banana all apply the same prompt-engineering rules.
"""


def _layer_strings(blueprint: dict) -> dict:
    kernel_parts = [blueprint["full_description"]]
    if blueprint["subject_details"]:
        kernel_parts.append(", ".join(blueprint["subject_details"]))
    if blueprint["subject_modifiers"]:
        kernel_parts.append(", ".join(blueprint["subject_modifiers"]))

    intent_parts = [blueprint["style_intent"], blueprint["mood"], blueprint["visual_style"], blueprint["era_period"]]
    medium_parts = [blueprint["camera"], blueprint["lens"], blueprint["film"], blueprint["rendering_engine"]]
    illum_parts = [blueprint["lighting"], blueprint["time_of_day"], blueprint["atmosphere"], blueprint["weather"]]
    format_parts = [blueprint["composition"], blueprint["angle"], blueprint["dof"], blueprint["color"]]

    return {
        "kernel": ", ".join(p for p in kernel_parts if p),
        "intent": ", ".join(p for p in intent_parts if p),
        "medium": ", ".join(p for p in medium_parts if p),
        "illumination": ", ".join(p for p in illum_parts if p),
        "format": ", ".join(p for p in format_parts if p),
    }


def compile_midjourney(blueprint: dict, params: dict) -> str:
    layers = _layer_strings(blueprint)
    content = ", ".join(v for v in layers.values() if v)

    # Manual UI params only override the inferred domain values when the
    # user actually changed them from the platform-neutral defaults.
    ar = params.get("ar", "1:1")
    if ar == "1:1":
        ar = blueprint["aspect_ratio"]
    stylize = params.get("s", 100)
    if stylize == 100:
        stylize = blueprint["stylize"]
    chaos = params.get("c", 0)
    if chaos == 0:
        chaos = blueprint["chaos"]
    weird = params.get("w", 0)
    quality = params.get("q", 1)

    suffix = [f"--ar {ar}"]
    if stylize != 100:
        suffix.append(f"--s {stylize}")
    if chaos != 0:
        suffix.append(f"--c {chaos}")
    if weird != 0:
        suffix.append(f"--w {weird}")
    if blueprint["raw"]:
        suffix.append("--raw")
    if quality != 1:
        suffix.append(f"--q {quality}")
    suffix.append("--v 8.1")

    return f"{content} {' '.join(suffix)}"


def compile_dalle(blueprint: dict) -> str:
    layers = _layer_strings(blueprint)
    desc = layers["kernel"]
    article = "an" if desc[:1].lower() in "aeiou" else "a"

    sentences = [f"Create an image of {article} {desc}."]
    if layers["intent"]:
        sentences.append(f"{layers['intent'].capitalize()}.")
    if layers["medium"]:
        sentences.append(f"Captured with {layers['medium']}.")
    if layers["illumination"]:
        sentences.append(f"{layers['illumination'].capitalize()}.")
    if layers["format"]:
        sentences.append(f"{layers['format'].capitalize()}.")
    sentences.append("Highly detailed, professional quality.")

    return " ".join(sentences)


def compile_nano_banana(blueprint: dict) -> str:
    layers = _layer_strings(blueprint)
    desc = layers["kernel"]

    parts = [f"Transform into a cinematic scene: {desc}."]
    if layers["intent"]:
        parts.append(f"{layers['intent'].capitalize()}.")
    if layers["medium"]:
        parts.append(f"Shot using {layers['medium']}.")
    if layers["illumination"]:
        parts.append(f"{layers['illumination'].capitalize()} sets the atmosphere.")
    if layers["format"]:
        parts.append(f"Strong {layers['format']} composition, striking environmental detail.")

    return " ".join(parts)
