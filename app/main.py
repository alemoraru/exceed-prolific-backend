from fastapi import FastAPI

from app.api import participants, code_submission, intervention

app = FastAPI(title="Error Message Study API")

app.include_router(participants.router, prefix="/api/participants", tags=["participants"])
app.include_router(code_submission.router, prefix="/api/code", tags=["code_submission"])
app.include_router(intervention.router, prefix="/api/intervention", tags=["intervention"])
