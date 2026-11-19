from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


# Creates connection to PostgreSQL
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)


# Creates database sessions
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    Create a database session for one request.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()