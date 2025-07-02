from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid

from app.db.session import SessionLocal
from app.db import models
from app.services.llm_intervention import get_intervention_message

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class InterventionRequest(BaseModel):
    participant_id: str
    snippet_id: str
    code: str
    error_msg: str
    intervention_type: str  # "pragmatic" or "contingent"


@router.post("/generate")
async def generate_intervention(req: InterventionRequest, db: Session = Depends(get_db)):
    message = get_intervention_message(req.code, req.error_msg, req.intervention_type)
    # log to DB
    iid = str(uuid.uuid4())
    record = models.Intervention(
        id=iid,
        participant_id=req.participant_id,
        snippet_id=req.snippet_id,
        code=req.code,
        error_msg=req.error_msg,
        intervention_type=req.intervention_type,
        intervention_msg=message
    )
    db.add(record)
    db.commit()
    return {"intervention": message}
