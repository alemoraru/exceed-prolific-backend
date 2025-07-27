from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import models
from app.db.session import get_db

router = APIRouter()


class EventRequest(BaseModel):
    """Model for logging events related to participants."""

    participant_id: str
    event_type: str
    timestamp: str


@router.post("/event")
async def log_event(request: EventRequest, db: Session = Depends(get_db)):
    """
    Log an event for a participant (e.g., window/tab switch, copy-paste).
    :param request: EventRequest containing participant_id, event_type, and timestamp
    :param db: Database session dependency
    :return: None
    """

    participant = db.get(models.Participant, request.participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found"
        )
    if not participant.consent:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Consent is required to record events.",
        )

    event = models.Event(
        participant_id=request.participant_id,
        event_type=request.event_type,
        timestamp=request.timestamp,
    )
    db.add(event)
    db.commit()
