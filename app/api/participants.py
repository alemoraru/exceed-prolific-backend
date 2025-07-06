from enum import Enum
from fastapi import APIRouter, Depends, HTTPException, status
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
    """Model for participant consent response."""
    consent: bool


class ConsentResult(BaseModel):
    """Model for the result of consent submission."""
    participant_id: str
    consent: bool


class ExperienceResponse(BaseModel):
    """Model for participant experience response."""
    participant_id: str
    python_yoe: int


class QuestionResponse(BaseModel):
    """Model for participant question response."""
    participant_id: str
    question_id: str
    answer: str


class QuestionId(Enum):
    """Enum for question IDs to ensure consistency."""
    Q1 = "q1"
    Q2 = "q2"
    Q3 = "q3"
    Q4 = "q4"
    Q5 = "q5"
    Q6 = "q6"
    Q7 = "q7"
    Q8 = "q8"


# TODO: Define correct answers for each question (perhaps in a config file)
CORRECT_ANSWERS = {
    QuestionId.Q1.value: "A",
    QuestionId.Q2.value: "B",
    QuestionId.Q3.value: "C",
    QuestionId.Q4.value: "D",
    QuestionId.Q5.value: "A",
    QuestionId.Q6.value: "B",
    QuestionId.Q7.value: "C",
    QuestionId.Q8.value: "D"
}


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
    if not participant.consent:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Consent is required to continue.")
    participant.python_yoe = response.python_yoe
    db.commit()
    return {"participant_id": response.participant_id}


@router.post("/question")
async def submit_question(response: QuestionResponse, db: Session = Depends(get_db)):
    participant = db.query(models.Participant).get(response.participant_id)

    # Validate participant, consent, and question ID
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    if not participant.consent:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Consent is required to continue.")
    if response.question_id not in QuestionId._value2member_map_:
        raise HTTPException(status_code=400, detail="Invalid question ID")

    # Prevent re-submission of the same question
    existing_answers = participant.answers or {}
    if response.question_id in existing_answers:
        raise HTTPException(status_code=400, detail="Question already answered")
    # Append new answer
    updated = {**existing_answers, response.question_id: response.answer}
    participant.answers = updated
    db.commit()

    # Skill level assignment logic
    if len(updated) == 8:
        correct_count = sum(
            1 for qid, ans in updated.items()
            if CORRECT_ANSWERS.get(qid) == ans
        )
        yoe = participant.python_yoe or 0
        skill_level = None
        if correct_count >= 6:
            skill_level = "expert"
        elif correct_count <= 3:
            skill_level = "novice"
        else:  # 4-5 correct
            skill_level = "expert" if yoe >= 5 else "novice"
        # Override for edge cases
        if correct_count >= 6 and yoe < 5:
            skill_level = "expert"
        if correct_count <= 3 and yoe >= 5:
            skill_level = "novice"
        participant.skill_level = skill_level
        db.commit()

    return {"participant_id": response.participant_id, "question_id": response.question_id}
