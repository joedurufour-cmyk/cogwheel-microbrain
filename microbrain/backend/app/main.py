import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.db import init_db
from app.engine.artifact_exporter import OUTPUTS_DIR
from app.middleware.observability import ObservabilityMiddleware
from app.middleware.security import SecurityMiddleware
from app.routes import mj81, reports, sessions, tests, turns

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


@app.get("/outputs/{filename}")
def serve_artifact(filename: str):
    # Prevent path traversal
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="invalid_filename")
    path = os.path.join(OUTPUTS_DIR, filename)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="artifact_not_found")
    return FileResponse(path, filename=filename)


app.include_router(mj81.router)
app.include_router(sessions.router)
app.include_router(turns.router)
app.include_router(reports.router)
app.include_router(tests.router)
