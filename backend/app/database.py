from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.config import get_settings
from app.models import Base

settings = get_settings()

# pool_pre_ping avoids "server closed the connection" after idle periods
engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: one session per request, always closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all_for_tests() -> None:
    """Only for local/test convenience (sqlite). Production schema comes
    from Alembic migrations — never call this against Postgres."""
    Base.metadata.create_all(bind=engine)
