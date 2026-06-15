from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DbSession

from app import models, schemas
from app.db import get_db
from app.engine.process import process_turn

router = APIRouter()


@router.post("/sessions/{session_id}/turns")
def create_turn(session_id: int, payload: schemas.TurnCreate, db: DbSession = Depends(get_db)):
    if not db.get(models.Session, session_id):
        raise HTTPException(status_code=404, detail="session_not_found")
    return process_turn(db, session_id, payload.raw_input)
