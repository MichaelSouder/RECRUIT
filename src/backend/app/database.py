from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import os

# Use SQLite for development if PostgreSQL is not available
database_url = settings.database_url
if "postgresql" in database_url:
    # Try to use SQLite as fallback if PostgreSQL connection fails
    try:
        # Test connection
        test_engine = create_engine(database_url, connect_args={"connect_timeout": 2})
        with test_engine.connect() as conn:
            pass
        engine = create_engine(database_url)
    except Exception:
        # Fallback to SQLite
        db_path = os.path.join(os.path.dirname(__file__), "..", "..", "recruit.db")
        database_url = f"sqlite:///{db_path}"
        engine = create_engine(database_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

