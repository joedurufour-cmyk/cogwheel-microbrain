from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.routes import reports, sessions, tests, turns

app = FastAPI(title="MicroBrain v0.3 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"ok": True}


app.include_router(sessions.router)
app.include_router(turns.router)
app.include_router(reports.router)
app.include_router(tests.router)
