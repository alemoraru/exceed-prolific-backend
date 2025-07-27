from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import code, events, feedback, participants
from app.core.config import FRONTEND_URL
from app.db.base import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(application: FastAPI):
    # Create tables once on startup
    Base.metadata.create_all(bind=engine)
    yield


# Initialize FastAPI app with lifespan context manager
app = FastAPI(title="Error Message Study API", lifespan=lifespan)

# Define & include API routers
app.include_router(
    participants.router, prefix="/api/participants", tags=["participants"]
)
app.include_router(code.router, prefix="/api/code", tags=["code"])
app.include_router(feedback.router, prefix="/api/errors", tags=["errors"])
app.include_router(events.router, prefix="/api/events", tags=["events"])

# Configure CORS
origins = [FRONTEND_URL]

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
