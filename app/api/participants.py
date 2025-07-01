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


class ConsentResponse(BaseModel):
    consent: bool


class ConsentResult(BaseModel):
    participant_id: str
    consent: bool


class ExperienceResponse(BaseModel):
    participant_id: str
    python_yoe: int


class QuestionResponse(BaseModel):
    participant_id: str
    question_id: str
    answer: str


@router.post("/consent", response_model=ConsentResult)
async def submit_consent(response: ConsentResponse, db: Session = Depends(get_db)):
    # Generate participant ID once at consent
    pid = str(uuid.uuid4())
    # Store initial record with consent flag
    participant = models.Participant(id=pid, python_yoe=None, skill_level=None, answers={}, consent=response.consent)
    db.add(participant)
    db.commit()
    return {"participant_id": pid, "consent": response.consent}


@router.post("/experience")
async def submit_experience(response: ExperienceResponse, db: Session = Depends(get_db)):
    # Must include existing participant_id
    participant = db.query(models.Participant).get(response.participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    participant.python_yoe = response.python_yoe
    db.commit()
    return {"participant_id": response.participant_id}


@router.post("/question")
async def submit_question(response: QuestionResponse, db: Session = Depends(get_db)):
    participant = db.query(models.Participant).get(response.participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    # Update answers JSON
    answers = participant.answers or {}
    answers[response.question_id] = response.answer
    participant.answers = answers
    db.commit()
    return {"participant_id": response.participant_id, "question_id": response.question_id}
