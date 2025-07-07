from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid

from app.db.session import SessionLocal
from app.db import models
from app.services.evaluator.evaluator import evaluate_code
from app.utils.enums import InterventionType
from app.data.snippets import get_snippet

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class CodeSubmission(BaseModel):
    """
    Model for code submission containing participant ID, snippet ID, and code.
    """
    participant_id: str
    snippet_id: str
    code: str


@router.post("/submit")
async def submit_code(submission: CodeSubmission, db: Session = Depends(get_db)):
    """
    Submit the user's code for compilation check and evaluation.
    :param submission: CodeSubmission model containing participant_id, snippet_id, and code.
    :param db: Database session dependency.
    :return: A dictionary with submission ID, status, and rephrased error message if any.
    """
    participant = db.query(models.Participant).get(submission.participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    if not participant.consent:
        raise HTTPException(status_code=403, detail="Consent is required to continue.")
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
    status, error = evaluate_code(
        submission.code,
        submission.snippet_id,
        InterventionType.CONTINGENT.value
    )

    sub.status = status
    sub.error_msg = error
    db.commit()

    return {"submission_id": sid, "status": status, "error_msg": error}


@router.get("/snippet/{snippet_id}")
def get_code_snippet(snippet_id: str, participant_id: str, db: Session = Depends(get_db)):
    """
    Retrieve the code snippet for a given snippet ID and participant ID.
    :param snippet_id: The ID of the code snippet to retrieve.
    :param participant_id: The ID of the participant requesting the snippet.
    :param db:  Database session dependency.
    :return: A dictionary containing the snippet ID, code, and respective standard error message.
    """
    participant = db.query(models.Participant).get(participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    if not participant.consent:
        raise HTTPException(status_code=403, detail="Consent is required to continue.")
    snippet = get_snippet(snippet_id)
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
    return {
        "id": snippet_id,
        "code": snippet["code"],
        "error": snippet["error"]
    }
