import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load backend/.env.neon explicitly.
# This file is located at backend/app/database.py, so parents[1] is backend/.
BACKEND_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = BACKEND_DIR / ".env.neon"

# For local development, make .env.neon take priority over any older
# DATABASE_URL already present in the PowerShell environment.
load_dotenv(dotenv_path=ENV_FILE, override=True)

# Read the database URL after loading the environment file.
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        f"DATABASE_URL is missing. Check the environment file: {ENV_FILE}"
    )

# Reuse database connections instead of opening a new connection per request.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
    pool_timeout=30,
    pool_recycle=300,
)

# Create database sessions.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for database models.
Base = declarative_base()


# Database connection dependency.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()