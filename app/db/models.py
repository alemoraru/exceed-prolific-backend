from sqlalchemy import JSON, Boolean, Column, Integer, String

from app.db.base import Base


class Participant(Base):
    """Model representing a participant in the study."""

    __tablename__ = "participants"
    id = Column(String, primary_key=True, index=True)
    consent = Column(Boolean, nullable=False)
    skill_level = Column(String, index=True, nullable=True)
    python_yoe = Column(Integer, nullable=True)
    answers = Column(JSON, nullable=True)
    mcq_questions = Column(JSON, nullable=True)
    mcq_answer_map = Column(JSON, nullable=True)


class Submission(Base):
    """Model representing a code submission by a participant."""

    __tablename__ = "submissions"
    id = Column(String, primary_key=True, index=True)
    participant_id = Column(String, index=True)
    snippet_id = Column(String)
    code = Column(String)
    status = Column(String)
    error_msg = Column(String)
