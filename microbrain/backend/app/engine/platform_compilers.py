"""Platform-specific prompt compilers.

Each compiler takes a VisualBlueprint dict (with full_description as base)
and formats it for the target platform.
"""


def compile_midjourney(blueprint: dict, params: dict) -> str:
    base = blueprint["full_description"]
    parts = [
        base,
        blueprint["style"],
        f"{blueprint['mood']} atmosphere",
        f"{blueprint['lighting']} lighting",
        blueprint["camera"],
        blueprint["quality"],
    ]
    content = ", ".join(p for p in parts if p)
    suffix = (
        f"--ar {params.get('ar', '1:1')} "
        f"--s {params.get('s', 100)} "
        f"--c {params.get('c', 0)} "
        f"--w {params.get('w', 0)} "
        f"--q {params.get('q', 1)} "
        "--v 8.1"
    )
    return f"{content} {suffix}"


def compile_dalle(blueprint: dict) -> str:
    desc = blueprint["full_description"]
    article = "an" if desc[0].lower() in "aeiou" else "a"
    lines = [
        f"Create an image of {article} {desc}.",
        f"{blueprint['style'].title()}.",
        f"{blueprint['mood'].title()} atmosphere.",
        f"{blueprint['lighting'].title()} lighting.",
        f"{blueprint['camera'].title()} composition.",
        "Highly detailed.",
    ]
    return " ".join(lines)


def compile_nano_banana(blueprint: dict) -> str:
    desc = blueprint["full_description"]
    return (
        f"Transform into a cinematic scene: {desc}. "
        f"{blueprint['style'].title()}. "
        f"{blueprint['mood'].title()} atmosphere with {blueprint['lighting']} lighting. "
        f"Strong {blueprint['camera']} composition, striking environmental detail."
    )
