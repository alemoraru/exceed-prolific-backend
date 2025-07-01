from fastapi import APIRouter, Depends
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


class QuestionResponse(BaseModel):
    participant_id: str | None = None
    question_id: str
    answer: str


class ExperienceResponse(BaseModel):
    participant_id: str | None = None
    python_yoe: int


@router.post("/question")
async def submit_question(response: QuestionResponse, db: Session = Depends(get_db)):
    # Create participant record if new
    pid = response.participant_id or str(uuid.uuid4())
    participant = db.query(models.Participant).get(pid)
    if not participant:
        participant = models.Participant(id=pid, python_yoe=None, skill_level=None, answers={})
        db.add(participant)
    # Update answers JSON
    answers = participant.answers or {}
    answers[response.question_id] = response.answer
    participant.answers = answers
    db.commit()
    return {"participant_id": pid, "question_id": response.question_id}


@router.post("/experience")
async def submit_experience(response: ExperienceResponse, db: Session = Depends(get_db)):
    pid = response.participant_id or str(uuid.uuid4())
    participant = db.query(models.Participant).get(pid)
    if not participant:
        participant = models.Participant(id=pid, python_yoe=response.python_yoe, skill_level=None, answers={})
        db.add(participant)
    else:
        participant.python_yoe = response.python_yoe
    db.commit()
    return {"participant_id": pid}
