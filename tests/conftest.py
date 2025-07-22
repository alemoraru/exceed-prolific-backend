import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker

from app.api import code_submission, events, participants
from app.db.base import Base
from app.main import app

# Use a file-based SQLite DB for thread safety in FastAPI tests
TEST_DB_URL = "sqlite:///./test_api.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Ensure tables are created
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override get_db for all routers that use it
app.dependency_overrides[participants.get_db] = override_get_db
app.dependency_overrides[code_submission.get_db] = override_get_db
app.dependency_overrides[events.get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    # Clean DB before each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    # Optionally, clean up after test
    # Base.metadata.drop_all(bind=engine)
