from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.data.snippets import get_snippet
from app.db import models
from app.db.session import SessionLocal
from app.services.evaluator.evaluator import evaluate_code

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class CodeSubmission(BaseModel):
    """
    Model for code submission containing participant ID, snippet ID, code, and time taken in ms.
    """

    participant_id: str
    snippet_id: str
    code: str
    time_taken_ms: int


@router.post("/submit")
async def submit_code(submission: CodeSubmission, db: Session = Depends(get_db)):
    """
    Submit the user's code for compilation check and evaluation.
    Records each attempt with attempt_number, error message shown, and evaluation status.
    :param submission: CodeSubmission model containing participant ID, snippet ID, and code.
    :param db: Database session dependency.
    :raises HTTPException: If participant does not exist, has not given consent, or intervention type is not assigned.
    :return: A dictionary containing participant ID, snippet ID, status, and error message.
    """
    participant = db.get(models.Participant, submission.participant_id)
    if not participant:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Participant not found")
    if not participant.consent:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail="Consent is required to continue."
        )
    if not participant.intervention_type:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Intervention type not assigned for participant.",
        )

    # Get PID and snippet ID from submission as they are required for evaluation
    pid = submission.participant_id
    snippet_id = submission.snippet_id

    # Determine attempt_number (increment for each new attempt)
    last_attempt = (
        db.query(models.CodeSubmission)
        .filter_by(participant_id=pid, snippet_id=snippet_id)
        .order_by(models.CodeSubmission.attempt_number.desc())
        .first()
    )
    attempt_number = 1 if not last_attempt else last_attempt.attempt_number + 1

    # Evaluate code (syntax + tests)
    code_status, llm_error_msg, tests_passed, tests_total = evaluate_code(
        submission.code, snippet_id, str(participant.intervention_type)
    )

    # Store the error message that was displayed to the user
    # in the database for analysis later
    if attempt_number == 1:
        # Always use static error for first attempt
        snippet = get_snippet(snippet_id)
        error_msg_displayed = snippet["error"] if snippet else ""
    else:
        # Use LLM error for follow-up attempts
        error_msg_displayed = llm_error_msg

    # Record the submission attempt
    sub = models.CodeSubmission(
        participant_id=pid,
        snippet_id=snippet_id,
        attempt_number=attempt_number,
        code=submission.code,
        error_msg_displayed=error_msg_displayed,
        status=code_status,
        tests_passed=tests_passed,
        tests_total=tests_total,
        time_taken_ms=submission.time_taken_ms,
    )
    db.add(sub)
    db.commit()

    return {
        "participant_id": pid,
        "snippet_id": snippet_id,
        "status": code_status,
        "error_msg": llm_error_msg,
    }


@router.get("/snippet/{snippet_id}")
def get_code_snippet(
    snippet_id: str, participant_id: str, db: Session = Depends(get_db)
):
    """
    Retrieve the code snippet for a given snippet ID and participant ID.
    :param snippet_id: The ID of the code snippet to retrieve.
    :param participant_id: The ID of the participant requesting the snippet.
    :param db: Database session dependency.
    :raises HTTPException: If participant does not exist, has not given consent, or snippet is not found.
    :return: A dictionary containing the snippet ID, code, and respective standard error message.
    """
    participant = db.get(models.Participant, participant_id)
    if not participant:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Participant not found")
    if not participant.consent:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail="Consent is required to continue."
        )
    snippet = get_snippet(snippet_id)

    if not snippet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Snippet not found")

    return {"id": snippet_id, "code": snippet["code"], "error": snippet["error"]}
