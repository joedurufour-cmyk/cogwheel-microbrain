"""Platform-specific prompt compilers.

Each compiler takes a VisualBlueprint dict and optional platform params,
and returns a formatted prompt string ready for that platform.
"""


def compile_midjourney(blueprint: dict, params: dict) -> str:
    subj = blueprint["subject"]
    action = blueprint["action"]
    env = blueprint["environment"]

    parts = []
    parts.append(f"{subj} {action}".strip() if action else subj)
    if env:
        parts.append(env)
    parts.append(blueprint["style"])
    parts.append(f"{blueprint['mood']} atmosphere")
    parts.append(f"{blueprint['lighting']} lighting")
    parts.append(blueprint["camera"])
    parts.append(blueprint["quality"])

    base = ", ".join(p for p in parts if p)
    suffix = (
        f"--ar {params.get('ar', '1:1')} "
        f"--s {params.get('s', 100)} "
        f"--c {params.get('c', 0)} "
        f"--w {params.get('w', 0)} "
        f"--q {params.get('q', 1)} "
        "--v 8.1"
    )
    return f"{base} {suffix}"


def compile_dalle(blueprint: dict) -> str:
    subj = blueprint["subject"]
    action = blueprint["action"]
    env = blueprint["environment"]

    subject_action = f"{subj} {action}".strip() if action else subj
    article = "an" if subject_action[0].lower() in "aeiou" else "a"
    env_article = "an" if env and env[0].lower() in "aeiou" else "a"
    env_clause = f" in {env_article} {env}" if env else ""

    lines = [
        f"Create an image of {article} {subject_action}{env_clause}.",
        f"{blueprint['style'].title()}.",
        f"{blueprint['mood'].title()} atmosphere.",
        f"{blueprint['lighting'].title()} lighting.",
        f"{blueprint['camera'].title()} composition.",
        "Highly detailed.",
    ]
    return " ".join(lines)


def compile_nano_banana(blueprint: dict) -> str:
    subj = blueprint["subject"]
    action = blueprint["action"]
    env = blueprint["environment"]

    subject_action = f"{subj} {action}".strip() if action else subj
    env_article = "an" if env and env[0].lower() in "aeiou" else "a"
    env_clause = f" in {env_article} {env}" if env else ""

    return (
        f"Transform into a cinematic scene: {subject_action}{env_clause}. "
        f"{blueprint['style'].title()}. "
        f"{blueprint['mood'].title()} atmosphere with {blueprint['lighting']} lighting. "
        f"Strong {blueprint['camera']} composition, striking environmental detail."
    )
