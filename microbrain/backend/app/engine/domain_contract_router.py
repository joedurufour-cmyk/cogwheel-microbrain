from app.domains.base import DomainContract
from app.domains.midjourney_v8_1 import MIDJOURNEY_V8_1_CONTRACT


SYSTEM_DESIGN_CONTRACT = DomainContract(
    domain_id="system_design_navigation",
    description="General system design navigation contract.",
    mandatory_keys=["objective", "central_object", "blocking_gap", "next_move"],
    inference_rules=["Keep the active narrative stable across turns."],
    constraints=["Do not repeat a resolved blocking gap."],
    output_schema={"answer": "string", "next_move": "string"},
)


def detect_domain(raw_input: str, extracted_objects: dict, narrative_state: dict) -> str:
    text = raw_input.lower()
    domain_state = narrative_state.get("domain_state") or {}
    if any(term in text for term in ["midjourney", "mj", "--ar", "--s", "--v", "render", "prompt"]):
        return "midjourney_v8_1_core"
    return domain_state.get("active_domain") or narrative_state.get("active_domain") or "system_design_navigation"


def load_domain_contract(domain_id: str) -> DomainContract:
    if domain_id == "midjourney_v8_1_core":
        return MIDJOURNEY_V8_1_CONTRACT
    return SYSTEM_DESIGN_CONTRACT

