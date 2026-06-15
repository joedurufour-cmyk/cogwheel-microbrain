# Cogwheel / MicroBrain v0.3

Full stack System Design Navigator.

## Purpose

Help a user build, audit, and evolve vertical systems without losing narrative, objective, architecture, risks, contradictions, or open loops.

## Stack

- Frontend: React, Vite, Tailwind, PWA
- Backend: FastAPI, Python
- Database: PostgreSQL through SQLAlchemy
- Deploy: Netlify frontend, Render/Railway/Fly backend, Supabase/Neon database
- LLM: none in v0.3

## Run Backend

```sh
cd microbrain/backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:DATABASE_URL="postgresql+psycopg://USER:PASSWORD@HOST:5432/DB"
uvicorn app.main:app --reload
```

For local engine/API tests without PostgreSQL, omit `DATABASE_URL`; the backend uses a local SQLite dev database.

## Run Frontend

```sh
cd microbrain/frontend
npm install
$env:VITE_API_BASE="http://localhost:8000"
npm run dev
```

For Netlify drag-and-drop, deploy the generated `microbrain/frontend/dist` contents. Do not drag the full source package unless Netlify is configured with base directory `microbrain/frontend`, build command `npm run build`, and publish directory `dist`.

## Test

```sh
cd microbrain/backend
pytest
```
