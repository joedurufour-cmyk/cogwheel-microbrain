# Operability

## Health

Backend:

```txt
GET /health
```

## Required API Checks

- `POST /sessions`
- `POST /sessions/{id}/turns`
- `GET /sessions/{id}/narrative`
- `GET /turns/{id}/report`
- `GET /sessions/{id}/export`
- `POST /tests/run`

## Memory Rule

The frontend is not primary memory. Narrative memory is persisted in PostgreSQL through:

- `sessions`
- `turns`
- `narrative_states`
- `turn_reports`
- `collisions`

## Developer Mode

Hidden by default.

Triggers:

- header icon
- `Ctrl+Shift+D`

Shows:

- Turn Report
- Narrative State
- Collision Detection
- Implication Engine
- Raw JSON
- Test Harness
- Export Session JSON
