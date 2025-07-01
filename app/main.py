from fastapi import FastAPI
from sqlalchemy import event
from app.db.session import engine
from app.api import participants, code_submission, intervention
from app.db.base import Base


# Automatically create tables at startup
@event.listens_for(engine, "connect")
def create_tables(dbapi_connection, connection_record):
    Base.metadata.create_all(bind=engine)


app = FastAPI(title="Error Message Study API")

app.include_router(participants.router, prefix="/api/participants", tags=["participants"])
app.include_router(code_submission.router, prefix="/api/code", tags=["code_submission"])
app.include_router(intervention.router, prefix="/api/intervention", tags=["intervention"])
