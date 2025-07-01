import os

DB_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
