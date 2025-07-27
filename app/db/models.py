from sqlalchemy import JSON, Boolean, Column, Integer, String

from app.db.base import Base


class Participant(Base):
    """Model representing a participant in the study."""

    __tablename__ = "participants"
    participant_id = Column(String, primary_key=True, index=True)
    consent = Column(Boolean, nullable=False)
    skill_level = Column(String, index=True, nullable=True)
    intervention_type = Column(String, nullable=True, index=True)
    python_yoe = Column(Integer, nullable=True)
    answers = Column(JSON, nullable=True)
    mcq_questions = Column(JSON, nullable=True)
    mcq_answer_map = Column(JSON, nullable=True)
    correct_mcq_count = Column(Integer, nullable=True)


class CodeSubmission(Base):
    """Model representing a code submission attempt by a participant for a snippet."""

    __tablename__ = "code_submissions"
    participant_id = Column(String, primary_key=True, index=True)
    snippet_id = Column(String, primary_key=True, index=True)
    attempt_number = Column(Integer, primary_key=True)
    code = Column(String)
    error_msg_displayed = Column(
        String
    )  # The error message shown to the user before this attempt
    status = Column(String)  # e.g., "success", "syntax_error", "test_failure"
    tests_passed = Column(Integer, nullable=True)
    tests_total = Column(Integer, nullable=True)
    time_taken_ms = Column(Integer, nullable=True)


class Event(Base):
    """Model representing a participant event (e.g., window/tab switch, copy-paste)."""

    __tablename__ = "events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    participant_id = Column(String, index=True, nullable=False)
    event_type = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)


class Feedback(Base):
    """Model representing Likert scale feedback for error messages after a code submission."""

    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, autoincrement=True)
    participant_id = Column(String, index=True, nullable=False)
    snippet_id = Column(String, index=True, nullable=False)
    attempt_number = Column(Integer, nullable=False)
    authoritativeness = Column(Integer, nullable=False)  # Likert scale 1-5
    cognitive_load = Column(Integer, nullable=False)  # Likert scale 1-5
    readability = Column(Integer, nullable=False)  # Likert scale 1-5
    timestamp = Column(String, nullable=False)
