import random
from datetime import UTC, datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.data.questions import get_randomized_questions_for_participant
from app.db import models
from app.db.models import Participant
from app.db.session import get_db
from app.utils.enums import InterventionType, SkillLevel

router = APIRouter()


class ConsentRequest(BaseModel):
    """Model for participant consent request."""

    participant_id: str
    consent: bool


class ConsentResponse(BaseModel):
    """Model for the response of consent submission."""

    participant_id: str
    consent: bool


class ExperienceRequest(BaseModel):
    """Model for participant experience response."""

    participant_id: str
    python_yoe: int


class ExperienceResponse(BaseModel):
    """Model for the response of participant experience submission."""

    participant_id: str


class QuestionRequest(BaseModel):
    """Model for participant question response."""

    participant_id: str
    question_id: str
    answer: str
    time_taken_ms: int


class QuestionResponse(BaseModel):
    """Model for the response of participant question submission."""

    participant_id: str
    question_id: str


class RevokeConsentRequest(BaseModel):
    """Model for request to revoke consent."""

    participant_id: str


class RevokeConsentResult(BaseModel):
    """Model for the result of consent revocation."""

    participant_id: str
    consent: bool


class ParticipantExistsRequest(BaseModel):
    """Model for checking if a participant exists."""

    participant_id: str


class ParticipantExistsResponse(BaseModel):
    """Model for the response of participant existence check."""

    exists: bool


class CompletionRedirectResponse(BaseModel):
    """Model for the response of completion redirect."""

    url: str


@router.get("/completion-redirect", response_model=CompletionRedirectResponse)
async def completion_redirect(participant_id: str, db: Session = Depends(get_db)):
    """
    Redirect to the completion page after all questions have been answered.
    :param participant_id: The ID of the participant completing the study.
    :param db: Database session dependency.
    :return: A message indicating successful completion.
    """
    participant = db.get(models.Participant, participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found"
        )
    if not participant.consent:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Consent is required to continue.",
        )
    if not participant.ended_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Participant has not completed the study yet.",
        )

    return {"url": "https://app.prolific.com/submissions/complete?cc=C1L0KIZE"}


@router.post("/participant-exists", response_model=ParticipantExistsResponse)
async def participant_exists(
    request: ParticipantExistsRequest, db: Session = Depends(get_db)
):
    """
    Check if a participant exists in the database.
    :param request: ParticipantExistsRequest model containing participant ID.
    :param db: Database session dependency.
    :return: ParticipantExistsResponse model indicating whether the participant exists.
    """
    exists = db.get(models.Participant, request.participant_id) is not None
    return {"exists": exists}


@router.post("/consent", response_model=ConsentResponse)
async def submit_consent(request: ConsentRequest, db: Session = Depends(get_db)):
    """
    Submit participant consent response. This endpoint is called when the participant clicks
    "I agree" or "I disagree" in the consent form of the application at the start of the study.
    :param request: ConsentResponse model containing participant ID and consent flag.
    :param db: Database session dependency.
    :return: ConsentResult model containing participant ID and consent flag.
    """

    # Use participant_id provided by the user (i.e., Prolific ID)
    pid = request.participant_id

    # Check if participant already exists
    existing_participant = db.get(models.Participant, pid)
    if existing_participant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Participant already exists. Use a different ID.",
        )

    # Create a new participant record with the provided consent and current timestamp
    now = datetime.now(UTC).isoformat()
    if request.consent:
        participant = models.Participant(
            participant_id=pid,
            answers={},
            consent=request.consent,
            started_at=now,
        )
    else:
        participant = models.Participant(
            participant_id=pid,
            answers={},
            consent=request.consent,
            started_at=now,
            ended_at=now,
        )

    db.add(participant)
    db.commit()
    return {"participant_id": pid, "consent": request.consent}


@router.post("/revoke-consent", response_model=RevokeConsentResult)
async def revoke_consent(request: RevokeConsentRequest, db: Session = Depends(get_db)):
    """
    Revoke consent for a participant. This endpoint is called when the participant
    decides to withdraw consent after initially agreeing. This will set the consent flag to False.
    :param request: RevokeConsentRequest model containing participant ID.
    :param db: Database session dependency.
    :return: RevokeConsentResult model containing participant ID and updated consent flag.
    """
    participant = db.get(models.Participant, request.participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found"
        )

    # Check if consent has already been revoked or declined
    if not participant.consent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consent has already been revoked or declined.",
        )

    # Update participant's consent status and ended_at timestamp
    now = datetime.now(UTC).isoformat()
    participant.ended_at = now
    participant.consent = False

    db.commit()
    return {"participant_id": request.participant_id, "consent": False}


@router.post("/experience", response_model=ExperienceResponse)
async def submit_experience(request: ExperienceRequest, db: Session = Depends(get_db)):
    """
    Submit participant's Python experience in years. This endpoint is called when the participant
    provides their years of experience in Python after consenting to the study.
    :param request: ExperienceResponse model containing participant ID and years of experience.
    :param db: Database session dependency.
    :return: Dictionary with participant ID.
    """

    # Must include existing participant_id
    participant = db.get(models.Participant, request.participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found"
        )
    if not participant.consent:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Consent is required to continue.",
        )
    participant.python_yoe = request.python_yoe
    db.commit()
    return {"participant_id": request.participant_id}


@router.get("/questions")
async def get_questions(participant_id: str, db: Session = Depends(get_db)):
    """
    Upon calling this endpoint, the participant will receive a set of randomized multiple-choice questions.
    This endpoint is called when the participant starts answering questions in the study.
    :param participant_id: The ID of the participant requesting questions.
    :param db: Database session dependency.
    :return: List of multiple-choice questions for the participant.
    """
    participant = db.get(models.Participant, participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found"
        )
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
        db.refresh(participant)

    return participant.mcq_questions


@router.post("/question", response_model=QuestionResponse)
async def submit_question(request: QuestionRequest, db: Session = Depends(get_db)):
    """
    Submit participant's answer to a multiple-choice question. This endpoint is called when the participant
    answers a question in the study. It validates the response, updates the participant's record,
    and assigns skill level and intervention type based on the answers (only after 8 questions have been answered).
    :param request: QuestionResponse model containing participant ID, question ID, answer index, and time taken in ms.
    :param db: Database session dependency.
    :return:
    """
    participant = db.get(models.Participant, request.participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found"
        )
    if not participant.consent:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Consent is required to continue.",
        )
    if (
        not participant.mcq_answer_map
        or request.question_id not in participant.mcq_answer_map
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MCQ answer map not found or question not served to participant",
        )
    # Prevent re-submission of the same question
    existing_answers = participant.answers or {}
    if request.question_id in existing_answers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Question already answered"
        )

    # Validate answer index
    try:
        submitted_index = int(request.answer)
    except Exception:
        # This case won't actually be reached, because the API will validate the type
        # and raise a 422 Unprocessable Entity error if the answer is not an integer.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Answer must be an integer index of the selected option",
        )
    updated = {
        **existing_answers,
        request.question_id: {
            "answer": submitted_index,
            "time_taken_ms": request.time_taken_ms,
        },
    }
    participant.answers = updated
    db.commit()
    db.refresh(participant)

    # If 8 questions have been answered, that means all questions have been answered,
    # and we can proceed with skill level and intervention type assignment
    if len(updated) == 8:
        assign_skill_and_intervention_and_snippet(participant, db)

    return {
        "participant_id": request.participant_id,
        "question_id": request.question_id,
    }


def assess_skill_level(correct_count: int, python_yoe: int) -> str:
    """
    Assess the skill level ("novice" or "expert") based on correct MCQ count and years of experience.
    :param correct_count: Number of correct answers given by the participant.
    :param python_yoe: Years of experience in Python programming, provided by the participant.
    """
    if correct_count >= 6:
        return SkillLevel.EXPERT.value
    elif correct_count <= 3:
        return SkillLevel.NOVICE.value
    else:  # 4-5 correct
        return SkillLevel.EXPERT.value if python_yoe >= 5 else SkillLevel.NOVICE.value


def get_skill_participants(db, skill_level: str) -> List[Participant]:
    """
    Returns all participants with the given skill level.
    """
    return (
        db.query(models.Participant)
        .filter(models.Participant.skill_level == skill_level)
        .all()
    )


def get_balanced_assignment(options: List[str], assigned_list: List[str]) -> str:
    """
    Given a list of options and a list of already assigned values, returns the least-assigned option (randomly among ties).
    :param options: List of possible options to assign.
    :param assigned_list: List of already assigned values for the same options.
    :return: A randomly chosen option from the least-assigned ones.
    """
    counts = {opt: 0 for opt in options}
    for val in assigned_list:
        if val in counts:
            counts[val] += 1
    min_count = min(counts.values())
    lowest = [opt for opt, cnt in counts.items() if cnt == min_count]
    return random.choice(lowest)


def assign_skill_and_intervention_and_snippet(participant, db: Session) -> None:
    """
    Assigns skill level, intervention type, and code snippet to a participant after MCQ answers and experience.
    Balances assignment by picking the least-assigned type/snippet, breaking ties randomly.
    Updates the participant object and commits to the database.
    :param participant: Participant model instance.
    :param db: Database session.
    """
    updated = participant.answers or {}
    correct_count = sum(
        1
        for qid, ans in updated.items()
        if participant.mcq_answer_map.get(qid) is not None
        and ans["answer"] == participant.mcq_answer_map[qid]
    )
    yoe = participant.python_yoe or 0
    skill_level = assess_skill_level(correct_count, yoe)
    participant.skill_level = skill_level
    participant.correct_mcq_count = correct_count

    if skill_level == SkillLevel.EXPERT.value:
        participant.snippet_id = "A"
        participant.intervention_type = InterventionType.CONTINGENT.value
    else:
        # Novice assignment: distribute among 5 allowed combinations
        allowed_combinations = [
            ("A", InterventionType.PRAGMATIC.value),
            ("B", InterventionType.CONTINGENT.value),
            ("C", InterventionType.PRAGMATIC.value),
            ("C", InterventionType.STANDARD.value),
            ("A", InterventionType.STANDARD.value),
        ]
        # Get all novices
        skill_participants = get_skill_participants(db, SkillLevel.NOVICE.value)
        assigned_combos = [
            (p.snippet_id, p.intervention_type) for p in skill_participants
        ]
        # Count each combo
        counts = {combo: 0 for combo in allowed_combinations}
        for combo in assigned_combos:
            if combo in counts:
                counts[combo] += 1
        min_count = min(counts.values())
        least_used = [combo for combo, cnt in counts.items() if cnt == min_count]
        chosen_combo = random.choice(least_used)
        participant.snippet_id, participant.intervention_type = chosen_combo

    db.commit()
    db.refresh(participant)
