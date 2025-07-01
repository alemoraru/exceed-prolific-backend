from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid

from app.db.session import SessionLocal
from app.db import models

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Part1Response(BaseModel):
    participant_id: str | None = None
    skill_level: str
    answers: dict[str, str]
    python_yoe: int


@router.post("/submit")
async def submit_part1_response(response: Part1Response, db: Session = Depends(get_db)):
    pid = response.participant_id or str(uuid.uuid4())
    participant = models.Participant(
        id=pid,
        skill_level=response.skill_level,
        python_yoe=response.python_yoe,
        answers=response.answers
    )
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return {"participant_id": pid}
