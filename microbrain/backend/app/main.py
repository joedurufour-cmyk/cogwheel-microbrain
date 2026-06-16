import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.middleware.observability import ObservabilityMiddleware
from app.middleware.security import SecurityMiddleware
from app.routes import reports, sessions, tests, turns

app = FastAPI(title="MicroBrain v0.3 API")

# Middlewares applied innermost-first; observability wraps everything outermost
app.add_middleware(ObservabilityMiddleware)
app.add_middleware(SecurityMiddleware)

frontend_origins = [
    origin.strip()
    for origin in os.getenv("FRONTEND_ORIGINS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_origin_regex=r"https://.*\.netlify\.app",
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "x-api-key", "x-trace-id"],
)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"ok": True, "service": "microbrain-api"}


app.include_router(sessions.router)
app.include_router(turns.router)
app.include_router(reports.router)
app.include_router(tests.router)
