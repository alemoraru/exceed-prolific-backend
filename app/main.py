from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import engine
from app.api import participants, code_submission
from app.db.base import Base
from app.core.config import PROLIFIC_FRONTEND_URL
import app.db.models as models

app = FastAPI(title="Error Message Study API")


@app.on_event("startup")
def on_startup():
    # Create tables once on startup
    Base.metadata.create_all(bind=engine)


app.include_router(participants.router, prefix="/api/participants", tags=["participants"])
app.include_router(code_submission.router, prefix="/api/code", tags=["code_submission"])

# Configure CORS
origins = [
    PROLIFIC_FRONTEND_URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health", "infra", "monitoring", "status"])
async def health_check():
    return {"status": "ok", "message": "API is running smoothly"}
