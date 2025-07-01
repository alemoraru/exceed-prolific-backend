from sqlalchemy import Column, String, Integer, Boolean, JSON
from app.db.base import Base


class Participant(Base):
    __tablename__ = "participants"
    id = Column(String, primary_key=True, index=True)
    consent = Column(Boolean, nullable=False)
    skill_level = Column(String, index=True, nullable=True)
    python_yoe = Column(Integer, nullable=True)
    answers = Column(JSON, nullable=True)


class Submission(Base):
    __tablename__ = "submissions"
    id = Column(String, primary_key=True, index=True)
    participant_id = Column(String, index=True)
    snippet_id = Column(String)
    code = Column(String)
    status = Column(String)
    error_msg = Column(String)


class Intervention(Base):
    __tablename__ = "interventions"
    id = Column(String, primary_key=True, index=True)
    participant_id = Column(String)
    snippet_id = Column(String)
    code = Column(String)
    error_msg = Column(String)
    intervention_type = Column(String)
    intervention_msg = Column(String)
