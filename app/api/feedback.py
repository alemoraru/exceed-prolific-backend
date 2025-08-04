from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import models
from app.db.session import get_db

router = APIRouter()


class ReadabilityFeedbackSubmission(BaseModel):
    """Model for readability feedback submission containing participant ID, snippet ID, and readability ratings."""

    participant_id: str
    snippet_id: str
    length: int
    jargon: int
    sentence_structure: int
    vocabulary: int
    time_taken_ms: int


class CognitiveLoadFeedbackSubmission(BaseModel):
    """Model for cognitive load feedback submission containing participant ID, snippet ID, and cognitive load ratings."""

    participant_id: str
    snippet_id: str
    intrinsic_load: int
    extraneous_load: int
    germane_load: int
    time_taken_ms: int


class AuthoritativenessFeedbackSubmission(BaseModel):
    """Model for authoritativeness feedback submission containing participant ID, snippet ID, and authoritativeness rating."""

    participant_id: str
    snippet_id: str
    authoritativeness: int
    time_taken_ms: int


class FeedbackSubmissionResponse(BaseModel):
    """Model for feedback submission response indicating success."""

    success: bool


def is_valid_likert(*args) -> bool:
    """
    Check if all provided Likert scale ratings are integers between 1 and 5.
    :param args: Variable length argument list of Likert ratings.
    :return: True if all ratings are valid, False otherwise.
    """
    return all(isinstance(x, int) and 1 <= x <= 5 for x in args)


def is_any_not_none(*args) -> bool:
    """
    Check if any of the provided arguments are not None.
    :param args: Variable length argument list.
    :return: True if any argument is not None, False otherwise.
    """
    return any(arg is not None for arg in args)


def get_feedback_entry(
    db: Session, participant_id: str, snippet_id: str
) -> models.Feedback | None:
    """
    Retrieve the feedback entry for a given participant and snippet.
    :param db: Database session.
    :param participant_id: ID of the participant.
    :param snippet_id: ID of the code snippet.
    :return: Feedback entry if found, None otherwise.
    """
    return (
        db.query(models.Feedback)
        .filter_by(participant_id=participant_id, snippet_id=snippet_id)
        .first()
    )


@router.post("/readability-feedback", response_model=FeedbackSubmissionResponse)
async def submit_readability_feedback(
    feedback: ReadabilityFeedbackSubmission, db: Session = Depends(get_db)
):
    """
    Submit readability feedback for an error message.
    :param feedback: ReadabilityFeedbackSubmission model containing participant ID, snippet ID, and readability ratings.
    :param db: Database session dependency.
    :return: A dictionary indicating success of the operation.
    """
    participant = db.get(models.Participant, feedback.participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    if not participant.consent:
        raise HTTPException(status_code=403, detail="Consent is required to continue.")
    if not is_valid_likert(
        feedback.length,
        feedback.jargon,
        feedback.sentence_structure,
        feedback.vocabulary,
    ):
        raise HTTPException(
            status_code=400,
            detail="All readability ratings must be integers between 1 and 5.",
        )

    # Try to retrieve existing feedback entry
    feedback_entry = get_feedback_entry(
        db, feedback.participant_id, feedback.snippet_id
    )

    # If no existing feedback entry, return 404
    if not feedback_entry:
        raise HTTPException(
            status_code=404, detail="Feedback entry not found for update"
        )
    # Check if any value already exists
    if is_any_not_none(
        feedback_entry.length,
        feedback_entry.jargon,
        feedback_entry.sentence_structure,
        feedback_entry.vocabulary,
    ):
        return {"success": False}

    feedback_entry.length = feedback.length
    feedback_entry.jargon = feedback.jargon
    feedback_entry.sentence_structure = feedback.sentence_structure
    feedback_entry.vocabulary = feedback.vocabulary
    feedback_entry.time_taken_ms_readability = feedback.time_taken_ms

    db.commit()
    return {"success": True}


@router.post("/cognitive-load-feedback", response_model=FeedbackSubmissionResponse)
async def submit_cognitive_load_feedback(
    feedback: CognitiveLoadFeedbackSubmission, db: Session = Depends(get_db)
):
    """
    Submit cognitive load feedback for an error message.
    :param feedback: CognitiveLoadFeedbackSubmission model containing participant ID, snippet ID, and cognitive load ratings.
    :param db: Database session dependency.
    :return: A dictionary indicating success of the operation.
    """
    participant = db.get(models.Participant, feedback.participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    if not participant.consent:
        raise HTTPException(status_code=403, detail="Consent is required to continue.")
    if not is_valid_likert(
        feedback.intrinsic_load, feedback.extraneous_load, feedback.germane_load
    ):
        raise HTTPException(
            status_code=400,
            detail="All cognitive load ratings must be integers between 1 and 5.",
        )

    # Try to retrieve existing feedback entry
    feedback_entry = get_feedback_entry(
        db, feedback.participant_id, feedback.snippet_id
    )

    # If no existing feedback entry, return 404
    if not feedback_entry:
        raise HTTPException(
            status_code=404, detail="Feedback entry not found for update"
        )
    # Check if any value already exists
    if is_any_not_none(
        feedback_entry.intrinsic_load,
        feedback_entry.extraneous_load,
        feedback_entry.germane_load,
    ):
        return {"success": False}

    feedback_entry.intrinsic_load = feedback.intrinsic_load
    feedback_entry.extraneous_load = feedback.extraneous_load
    feedback_entry.germane_load = feedback.germane_load
    feedback_entry.time_taken_ms_cognitive_load = feedback.time_taken_ms

    db.commit()
    return {"success": True}


@router.post("/authoritativeness-feedback", response_model=FeedbackSubmissionResponse)
async def submit_authoritativeness_feedback(
    feedback: AuthoritativenessFeedbackSubmission, db: Session = Depends(get_db)
):
    """
    Submit authoritativeness feedback for an error message.
    :param feedback: AuthoritativenessFeedbackSubmission model containing participant ID, snippet ID, and authoritativeness rating.
    :param db: Database session dependency.
    :return: A dictionary indicating success of the operation.
    """
    participant = db.get(models.Participant, feedback.participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    if not participant.consent:
        raise HTTPException(status_code=403, detail="Consent is required to continue.")
    if not is_valid_likert(feedback.authoritativeness):
        raise HTTPException(
            status_code=400,
            detail="Authoritativeness rating must be an integer between 1 and 5.",
        )

    # Try to retrieve existing feedback entry
    feedback_entry = get_feedback_entry(
        db, feedback.participant_id, feedback.snippet_id
    )

    # If no existing feedback entry, return 404
    if not feedback_entry:
        raise HTTPException(
            status_code=404, detail="Feedback entry not found for update"
        )
    # Check if value already exists
    if is_any_not_none(feedback_entry.authoritativeness):
        return {"success": False}

    feedback_entry.authoritativeness = feedback.authoritativeness
    feedback_entry.time_taken_ms_authoritativeness = feedback.time_taken_ms
    db.commit()

    # Set ended_at for participant
    participant = db.get(models.Participant, feedback.participant_id)
    if participant:
        participant.ended_at = datetime.now(UTC).isoformat()
        db.commit()

    return {"success": True}
