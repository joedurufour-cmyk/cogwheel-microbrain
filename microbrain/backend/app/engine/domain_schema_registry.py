from typing import Any

from pydantic import create_model


DOMAIN_SCHEMA_CATALOG: dict[str, dict[str, type]] = {
    "midjourney_v8_1_core": {
        "aspect_ratio": str,
        "stylize": int,
        "version": str,
    },
    "legal_contracts_core": {
        "penalty_clause": str,
        "deposit_months": int,
    },
}


def inject_domain_schema(domain_id: str, fallback_parameters: dict[str, Any] | None = None):
    fields = DOMAIN_SCHEMA_CATALOG.get(domain_id)
    if not fields:
        fields = infer_fields_from_parameters(fallback_parameters or {})
    return create_model(f"{domain_id}_Schema", **{key: (field_type, ...) for key, field_type in fields.items()})


def infer_fields_from_parameters(parameters: dict[str, Any]) -> dict[str, type]:
    fields = {}
    for key, value in parameters.items():
        if isinstance(value, bool):
            fields[key] = bool
        elif isinstance(value, int):
            fields[key] = int
        elif isinstance(value, float):
            fields[key] = float
        elif isinstance(value, list):
            fields[key] = list
        elif isinstance(value, dict):
            fields[key] = dict
        else:
            fields[key] = str
    return fields or {"raw_parameters": dict}

