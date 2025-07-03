from enum import Enum
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid

from app.db.session import SessionLocal
from app.db import models
from app.services.evaluator.evaluator import evaluate_code


class InterventionType(Enum):
    """Enum for intervention types."""
    PRAGMATIC = "pragmatic"
    CONTINGENT = "contingent"


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class CodeSubmission(BaseModel):
    participant_id: str
    snippet_id: str
    code: str


@router.post("/submit")
async def submit_code(submission: CodeSubmission, db: Session = Depends(get_db)):
    sid = str(uuid.uuid4())
    sub = models.Submission(
        id=sid,
        participant_id=submission.participant_id,
        snippet_id=submission.snippet_id,
        code=submission.code,
        status="pending",
        error_msg=None
    )
    db.add(sub)
    db.commit()
    # Evaluate code (syntax + tests)
    status, error = evaluate_code(submission.code, submission.snippet_id, InterventionType.CONTINGENT.value)
    sub.status = status
    sub.error_msg = error
    db.commit()

    return {"submission_id": sid, "status": status, "error_msg": error}
