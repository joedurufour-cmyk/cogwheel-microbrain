# System Contract

## Domain

System Design Navigation.

## Core Pipeline

```txt
input
-> narrative_model
-> inferred_intent
-> collision_detection
-> implication_engine
-> response_plan
-> answer
```

## Hard Rule

```py
if not response_plan:
    raise Exception("NO_RESPONSE_PLAN")
```

## Turn Contract v0.3

Every backend turn returns:

```json
{
  "raw_input": "",
  "segments": [],
  "narrative_model": {},
  "mental_model": {},
  "inferred_intent": {
    "explicit": null,
    "latent": null,
    "confidence": 0
  },
  "collision_detection": {
    "exists": false,
    "type": "none",
    "severity": 0,
    "evidence": []
  },
  "implication_engine": {
    "implications": [],
    "risks": [],
    "next_best_move": ""
  },
  "response_plan": {
    "move": "",
    "purpose": "",
    "must_include": [],
    "must_avoid": []
  },
  "answer": "",
  "report": {
    "what_i_detected": [],
    "what_i_updated_in_memory": [],
    "narrative_before": {},
    "narrative_after": {},
    "collisions_found": [],
    "implication_used": [],
    "response_plan": {},
    "answer_given": ""
  }
}
```

## Non Clinical KB Constraint

The cognitive KB uses conversational inference patterns only:

- narrative cognition
- mental models
- intent recognition
- conversational repair
- cognitive load
- decision-making
- metacognition
- reasoning patterns
- attention/salience
- dialogue acts

It must not diagnose, label the user clinically, or position the product as therapy.
