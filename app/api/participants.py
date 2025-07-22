import random

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.data.questions import get_randomized_questions_for_participant
from app.db import models
from app.db.session import SessionLocal
from app.utils.enums import InterventionType, SkillLevel

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


class QuestionRequest(BaseModel):
    """Model for participant question response."""

    participant_id: str
    question_id: str
    answer: str
    time_taken_ms: int


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
    exists = db.query(models.Participant).get(request.participant_id) is not None
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

    # Store initial record with consent flag
    participant = models.Participant(
        participant_id=pid,
        answers={},
        consent=request.consent,
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
    participant = db.query(models.Participant).get(request.participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    # Check if consent is already revoked / declined
    if not participant.consent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consent has already been revoked or declined.",
        )

    participant.consent = False
    db.commit()
    return {"participant_id": request.participant_id, "consent": False}


@router.post("/experience")
async def submit_experience(request: ExperienceRequest, db: Session = Depends(get_db)):
    """
    Submit participant's Python experience in years. This endpoint is called when the participant
    provides their years of experience in Python after consenting to the study.
    :param request: ExperienceResponse model containing participant ID and years of experience.
    :param db: Database session dependency.
    :return: Dictionary with participant ID.
    """

    # Must include existing participant_id
    participant = db.query(models.Participant).get(request.participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
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
async def submit_question(request: QuestionRequest, db: Session = Depends(get_db)):
    """
    Submit participant's answer to a multiple-choice question. This endpoint is called when the participant
    answers a question in the study. It validates the response, updates the participant's record,
    and assigns skill level and intervention type based on the answers (only after 8 questions have been answered).
    :param request: QuestionResponse model containing participant ID, question ID, answer index, and time taken in ms.
    :param db: Database session dependency.
    :return:
    """
    participant = db.query(models.Participant).get(request.participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
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
            status_code=400,
            detail="MCQ answer map not found or question not served to participant",
        )
    # Prevent re-submission of the same question
    existing_answers = participant.answers or {}
    if request.question_id in existing_answers:
        raise HTTPException(status_code=400, detail="Question already answered")

    # Validate answer index
    try:
        submitted_index = int(request.answer)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Answer must be an integer index of the selected option",
        )
    correct_index = participant.mcq_answer_map[request.question_id]
    is_correct = submitted_index == correct_index
    updated = {
        **existing_answers,
        request.question_id: {
            "answer": submitted_index,
            "time_taken_ms": request.time_taken_ms,
        },
    }
    participant.answers = updated
    db.commit()

    # If 8 questions have been answered, that means all questions have been answered,
    # and we can proceed with skill level and intervention type assignment
    if len(updated) == 8:
        assign_skill_and_intervention(participant, db)

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


def assign_intervention_type(contingent_count: int, pragmatic_count: int) -> str:
    """
    Assign intervention type to balance the groups, breaking ties randomly.
    :param contingent_count: Number of participants who were assigned the CONTINGENT intervention.
    :param pragmatic_count: Number of participants who were assigned the PRAGMATIC intervention.
    :return: Assigned intervention type as a string.
    """
    if contingent_count < pragmatic_count:
        return InterventionType.CONTINGENT.value
    elif pragmatic_count < contingent_count:
        return InterventionType.PRAGMATIC.value
    else:
        return random.choice(
            [InterventionType.CONTINGENT.value, InterventionType.PRAGMATIC.value]
        )


def assign_skill_and_intervention(participant, db) -> None:
    """
    Assigns skill level and intervention type to a participant based on their MCQ answers and experience.
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

    # --- InterventionType assignment logic ---
    skill_participants = (
        db.query(models.Participant)
        .filter(
            models.Participant.skill_level == skill_level,
            models.Participant.intervention_type != None,
        )
        .all()
    )
    contingent_count = sum(
        1
        for p in skill_participants
        if p.intervention_type == InterventionType.CONTINGENT.value
    )
    pragmatic_count = sum(
        1
        for p in skill_participants
        if p.intervention_type == InterventionType.PRAGMATIC.value
    )
    assigned_type = assign_intervention_type(contingent_count, pragmatic_count)
    participant.intervention_type = assigned_type
    db.commit()
