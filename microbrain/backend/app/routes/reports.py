import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DbSession

from app import models
from app.db import get_db

router = APIRouter()


@router.get("/turns/{turn_id}/report")
def get_report(turn_id: int, db: DbSession = Depends(get_db)):
    report = db.query(models.TurnReport).filter(models.TurnReport.turn_id == turn_id).one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="report_not_found")
    return json.loads(report.report_json)
