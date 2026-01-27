import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Railway provides DATABASE_URL. 
# Default to sqlite for local testing if env var is missing.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./macro_data.db")

# Fix for "postgres://" in older sqlalchemy versions if railway sends that (they often do)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
# check_same_thread is needed for SQLite, but causes issues with Postgres. 
# We can make the args conditional or just rely on default for Postgres.
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

# Re-create engine with args if needed, but for simplicity/robustness:
if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
