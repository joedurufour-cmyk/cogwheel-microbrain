DOMAIN = "System Design Navigation"

DOMAIN_OBJECTS = [
    "objective",
    "architecture",
    "module",
    "dependency",
    "contract",
    "assumption",
    "risk",
    "bottleneck",
    "contradiction",
    "implementation_step",
    "validation",
    "open_loop",
]

COLLISION_TYPES = [
    "goal_drift",
    "architecture_drift",
    "scope_explosion",
    "hidden_dependency",
    "contract_violation",
    "implementation_without_design",
    "design_without_validation",
    "validation_without_metrics",
    "missing_context",
    "over_inference",
]

MOVES = [
    "align",
    "warn",
    "decompose",
    "correct",
    "test",
    "freeze_contract",
    "propose_next_step",
    "summarize",
]

CONCEPTUAL_BASE = [
    "narrative cognition",
    "mental models",
    "intent recognition",
    "conversational repair",
    "cognitive load",
    "decision-making",
    "metacognition",
    "reasoning patterns",
    "attention/salience",
    "dialogue acts",
]

TEST_INPUTS = [
    "quiero construir un micro cerebro conversador",
    "esto no mantiene el hilo",
    "no es sandbox, debe ser reconstruible",
    "quiero llevarlo a codigo sin perder contrato",
    "estamos agregando cosas pero no validamos",
    "la narrativa original era construir un motor, no un chatbot",
    "hay demasiada informacion visible para el usuario",
    "quiero probarlo en sistemas verticales",
    "me preocupa que sobreinfiera",
    "estoy mezclando diseno, validacion, codigo y frustracion",
    "agreguemos mas tabs y mas debug",
    "necesito saber cual es el siguiente movimiento",
    "vamos a produccion sin metricas",
    "corrige la arquitectura antes del deploy",
    "hay dependencias ocultas entre memoria y respuesta",
    "resumelo para cerrar el loop",
    "quiero implementar el backend ya",
    "la UI esta limpia pero el motor deriva",
    "falta congelar el contrato narrativo",
    "validemos el engine con casos verticales",
    "el objetivo cambio a chatbot general",
    "la memoria no debe ser localStorage",
    "necesito exportar el reporte interno",
    "hay mucho scope nuevo en esta version",
    "el sistema debe auditar contradicciones",
]


def normalize(text: str) -> str:
    replacements = str.maketrans("áéíóúüñÁÉÍÓÚÜÑ", "aeiouunAEIOUUN")
    return text.translate(replacements).lower()


def has_any(text: str, terms: list[str]) -> bool:
    normalized = normalize(text)
    return any(normalize(term) in normalized for term in terms)


def unique(items):
    seen = []
    for item in items:
        if item and item not in seen:
            seen.append(item)
    return seen
