from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid

from app.db.session import SessionLocal
from app.db import models
from app.data.questions import get_randomized_questions_for_participant

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
    time_taken_ms: int


@router.post("/consent", response_model=ConsentResult)
async def submit_consent(response: ConsentResponse, db: Session = Depends(get_db)):
    # Generate participant ID once at consent
    pid = str(uuid.uuid4())
    # Store initial record with consent flag
    participant = models.Participant(
        id=pid, python_yoe=None, skill_level=None, answers={}, consent=response.consent
    )
    db.add(participant)
    db.commit()
    return {"participant_id": pid, "consent": response.consent}


@router.post("/experience")
async def submit_experience(
    response: ExperienceResponse, db: Session = Depends(get_db)
):
    # Must include existing participant_id
    participant = db.query(models.Participant).get(response.participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    if not participant.consent:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Consent is required to continue.",
        )
    participant.python_yoe = response.python_yoe
    db.commit()
    return {"participant_id": response.participant_id}


@router.get("/questions")
async def get_questions(participant_id: str, db: Session = Depends(get_db)):
    """
    Serve the same randomized multiple-choice questions for a participant on every call.
    On first call, randomize and store in the participant record. On subsequent calls, return the stored set.
    """
    participant = db.query(models.Participant).get(participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    if not participant.consent:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Consent is required to continue.",
        )

    # Only randomize and store in DB if not already present
    if (
        not participant.mcq_answer_map
        or not hasattr(participant, "mcq_questions")
        or participant.mcq_questions is None
    ):
        questions, answer_map = get_randomized_questions_for_participant()
        participant.mcq_answer_map = answer_map
        participant.mcq_questions = questions
        db.commit()

    return participant.mcq_questions


@router.post("/question")
async def submit_question(response: QuestionResponse, db: Session = Depends(get_db)):
    participant = db.query(models.Participant).get(response.participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    if not participant.consent:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Consent is required to continue.",
        )
    if (
        not participant.mcq_answer_map
        or response.question_id not in participant.mcq_answer_map
    ):
        raise HTTPException(
            status_code=400,
            detail="MCQ answer map not found or question not served to participant",
        )
    # Prevent re-submission of the same question
    existing_answers = participant.answers or {}
    if response.question_id in existing_answers:
        raise HTTPException(status_code=400, detail="Question already answered")

    # Validate answer index
    try:
        submitted_index = int(response.answer)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Answer must be an integer index of the selected option",
        )
    correct_index = participant.mcq_answer_map[response.question_id]
    is_correct = submitted_index == correct_index
    updated = {
        **existing_answers,
        response.question_id: {
            "answer": submitted_index,
            "time_taken_ms": response.time_taken_ms,
        },
    }
    participant.answers = updated
    db.commit()

    # Skill level assignment logic
    if len(updated) == 8:
        correct_count = sum(
            1
            for qid, ans in updated.items()
            if participant.mcq_answer_map.get(qid) is not None
            and ans["answer"] == participant.mcq_answer_map[qid]
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

    return {
        "participant_id": response.participant_id,
        "question_id": response.question_id,
    }
