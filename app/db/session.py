from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import DB_URL

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency that provides a database session for each request.
    Yields a database session and ensures it is closed after use.
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
