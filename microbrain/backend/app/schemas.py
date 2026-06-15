from typing import Any

from pydantic import BaseModel


class SessionCreate(BaseModel):
    title: str | None = None


class SessionOut(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True


class TurnCreate(BaseModel):
    raw_input: str


class TurnContractOut(BaseModel):
    raw_input: str
    segments: list[dict[str, Any]]
    narrative_model: dict[str, Any]
    mental_model: dict[str, Any]
    inferred_intent: dict[str, Any]
    collision_detection: dict[str, Any]
    implication_engine: dict[str, Any]
    response_plan: dict[str, Any]
    answer: str
    report: dict[str, Any]


class TestRunOut(BaseModel):
    total: int
    passed: int
    failed: int
    failed_cases: list[dict[str, Any]]
