from __future__ import annotations

import logging
import time
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, class_=Session)


def init_db(retries: int = 15, delay_seconds: float = 2.0) -> None:
    from app.models.claim_record import ClaimRecord

    last_error = None
    for attempt in range(1, retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database initialized.")
            return
        except Exception as exc:  # pragma: no cover - startup resilience
            last_error = exc
            logger.warning("Database init attempt %s/%s failed: %s", attempt, retries, exc)
            time.sleep(delay_seconds)

    raise RuntimeError(f"Could not initialize database after {retries} attempts: {last_error}")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
