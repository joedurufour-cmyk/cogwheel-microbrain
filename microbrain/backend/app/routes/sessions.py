from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DbSession

from app import models, schemas
from app.db import get_db
from app.engine.process import load_narrative

router = APIRouter()


@router.post("/sessions", response_model=schemas.SessionOut)
def create_session(payload: schemas.SessionCreate, db: DbSession = Depends(get_db)):
    session = models.Session(title=payload.title or "System Design Session")
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/sessions/{session_id}", response_model=schemas.SessionOut)
def get_session(session_id: int, db: DbSession = Depends(get_db)):
    session = db.get(models.Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="session_not_found")
    return session


@router.get("/sessions/{session_id}/narrative")
def get_narrative(session_id: int, db: DbSession = Depends(get_db)):
    if not db.get(models.Session, session_id):
        raise HTTPException(status_code=404, detail="session_not_found")
    return load_narrative(db, session_id)


@router.get("/sessions/{session_id}/export")
def export_session(session_id: int, db: DbSession = Depends(get_db)):
    session = db.get(models.Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="session_not_found")
    turns = db.query(models.Turn).filter(models.Turn.session_id == session_id).order_by(models.Turn.id).all()
    collisions = db.query(models.Collision).filter(models.Collision.session_id == session_id).all()
    return {
        "session": {"id": session.id, "title": session.title},
        "narrative": load_narrative(db, session_id),
        "turns": [{"id": turn.id, "raw_input": turn.raw_input, "answer": turn.answer} for turn in turns],
        "collisions": [
            {"type": item.collision_type, "severity": item.severity, "evidence_json": item.evidence_json}
            for item in collisions
        ],
    }
