import os

DB_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# backend/app/db/base.py
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
