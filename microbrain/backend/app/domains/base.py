from typing import Any

from pydantic import BaseModel


class DomainContract(BaseModel):
    domain_id: str
    description: str
    mandatory_keys: list[str]
    inference_rules: list[str]
    constraints: list[str]
    output_schema: dict[str, Any]

