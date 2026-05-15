from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sqlite3
from pathlib import Path

from config import settings

# Application database engine
# check_same_thread=False is needed for SQLite to allow multiple threads to interact with the database,
# which is common in web applications.
app_engine = create_engine(
    settings.database_url, connect_args={"check_same_thread": False}
)

# Demo database engine (read-only)
def get_demo_engine():
    # Extract path from database_url and handle relative path if any
    path = settings.demo_db_url.replace("sqlite:///", "")

    BASE_DIR = Path(__file__).resolve().parent.parent
    full_path = BASE_DIR / path.replace("./", "")
    # Custom connection function for read-only SQLite
    def create_ro_connection():
        return sqlite3.connect(f"file:{full_path}?mode=ro", uri=True)

    # create_engine does not directly support custom connection functions in the same way
    # as for app_engine. For a read-only demo DB, direct sqlite3 usage is more straightforward
    # for simplicity, we will just expose the path and let consumers use sqlite3 directly for now
    # as SQLAlchemy engines for read-only are more complex and might not be strictly needed here.
    # For now, demo_db_path will be used by consumers to create direct sqlite3 connections.
    return str(full_path) # Return path to demo DB

demo_db_path = get_demo_engine()


# SessionLocal for application database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=app_engine)

Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
