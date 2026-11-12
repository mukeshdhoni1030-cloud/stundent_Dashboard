
import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load .env file
load_dotenv()

# Read database URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing in .env")

# Create PostgreSQL connection
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# Create database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for database models
Base = declarative_base()


# Database connection dependency
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
