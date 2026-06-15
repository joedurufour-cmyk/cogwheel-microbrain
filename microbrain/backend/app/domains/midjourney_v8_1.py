from app.domains.base import DomainContract


MIDJOURNEY_V8_1_CONTRACT = DomainContract(
    domain_id="midjourney_v8_1_core",
    description="Prompt generation system for Midjourney v8.1 renders.",
    mandatory_keys=[
        "input_mode",
        "output_format",
        "aspect_ratio",
        "stylization_level",
        "lighting_model",
        "base_positive_prompt",
        "technical_parameters",
    ],
    inference_rules=[
        "If user mentions cinematic, infer aspect_ratio candidate 16:9 or 21:9.",
        "If user mentions portrait, infer aspect_ratio candidate 2:3 or 4:5.",
        "If user mentions product render, infer clean studio lighting.",
        "If user mentions architecture/interior, infer wide angle or architectural photography grammar.",
        "If user mentions v8.1, require --v 8.1 in technical_parameters.",
    ],
    constraints=[
        "Do not generate final prompt until output_format is defined.",
        "Do not ask again for a gap already resolved.",
        "Do not expose internal domain contract to normal user.",
        "Never invent unsupported Midjourney parameters.",
    ],
    output_schema={
        "positive_prompt": "string",
        "negative_prompt": "string | optional",
        "parameters": {
            "aspect_ratio": "string",
            "stylize": "number | optional",
            "chaos": "number | optional",
            "version": "8.1",
        },
    },
)

