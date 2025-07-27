from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import models
from app.db.session import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ErrorFeedbackSubmission(BaseModel):
    """Model for submitting Likert scale feedback for error messages shown after code submission attempts."""

    participant_id: str
    snippet_id: str
    attempt_number: int
    authoritativeness: int
    cognitive_load: int
    readability: int
    timestamp: str


@router.post("/feedback")
async def submit_feedback(
    feedback: ErrorFeedbackSubmission, db: Session = Depends(get_db)
):
    """
    Submit Likert scale feedback for the error message shown after a code submission attempt.
    :param feedback: ErrorFeedbackSubmission model containing participant ID, snippet ID, attempt number, and feedback.
    :param db: Database session dependency.
    :raises HTTPException: If participant does not exist, has not given consent, or submission does not exist.
    """

    participant = db.get(models.Participant, feedback.participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    if not participant.consent:
        raise HTTPException(status_code=403, detail="Consent is required to continue.")

    # Optionally, check that the submission exists
    submission = (
        db.query(models.CodeSubmission)
        .filter_by(
            participant_id=feedback.participant_id,
            snippet_id=feedback.snippet_id,
            attempt_number=feedback.attempt_number,
        )
        .first()
    )
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found for feedback")

    error_feedback = models.Feedback(
        participant_id=feedback.participant_id,
        snippet_id=feedback.snippet_id,
        attempt_number=feedback.attempt_number,
        authoritativeness=feedback.authoritativeness,
        cognitive_load=feedback.cognitive_load,
        readability=feedback.readability,
        timestamp=feedback.timestamp,
    )

    db.add(error_feedback)
    db.commit()
    return {"success": True}
