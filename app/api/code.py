from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.data.snippets import get_snippet
from app.db import models
from app.db.session import get_db
from app.services.evaluator.evaluator import evaluate_code
from app.services.llm.intervention import get_rephrased_error_message
from app.utils.enums import InterventionType

router = APIRouter()


class CodeSubmission(BaseModel):
    """
    Model for code submission containing participant ID, snippet ID, code, and time taken in ms.
    """

    participant_id: str
    snippet_id: str
    code: str
    time_taken_ms: int


@router.post("/submit")
async def submit_code_fix(submission: CodeSubmission, db: Session = Depends(get_db)):
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
    if not participant.snippet_id:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Code snippet not assigned for participant.",
        )
    if submission.snippet_id != participant.snippet_id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="You can only submit code for your assigned snippet.",
        )

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

    # Enforce maximum of 3 attempts
    if attempt_number > 3:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Maximum number of attempts (3) reached for this snippet.",
        )

    # Evaluate code (syntax + tests)
    code_status, llm_error_msg, tests_passed, tests_total = evaluate_code(
        submission.code, snippet_id
    )

    # Record the submission attempt
    sub = models.CodeSubmission(
        participant_id=pid,
        snippet_id=snippet_id,
        attempt_number=attempt_number,
        code=submission.code,
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


@router.get("/snippet")
def get_code_and_error(participant_id: str, db: Session = Depends(get_db)):
    """
    Retrieve the code snippet and error message for the participant's assigned snippet.
    :param participant_id: The ID of the participant requesting the snippet.
    :param db: Database session dependency.
    :raises HTTPException: If participant does not exist, has not given consent, or snippet is not found.
    :return: A dictionary containing the snippet ID, code, and respective error message.
    """
    participant = db.get(models.Participant, participant_id)
    if not participant:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Participant not found")
    if not participant.consent:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail="Consent is required to continue."
        )
    if not participant.snippet_id:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Code snippet not assigned for participant.",
        )

    snippet_id = str(participant.snippet_id)
    if participant.snippet_id != snippet_id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="You can only retrieve your assigned snippet.",
        )

    # Fetch the snippet from the data source
    snippet = get_snippet(snippet_id)
    if not snippet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Snippet not found")

    code = snippet["code"]
    error = snippet["error"]
    intervention_type = participant.intervention_type
    markdown = False
    if (
        intervention_type == InterventionType.PRAGMATIC.value
        or intervention_type == InterventionType.CONTINGENT.value
    ):
        error = get_rephrased_error_message(
            code, error, InterventionType(intervention_type).value
        )
        markdown = True
    feedback_entry = models.Feedback(
        participant_id=participant_id,
        snippet_id=snippet_id,
        error_message=error,
    )
    db.add(feedback_entry)
    db.commit()

    return {"id": snippet_id, "code": code, "error": error, "markdown": markdown}
