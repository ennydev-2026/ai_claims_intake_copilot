from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class ClaimRecord(Base):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    claim_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    customer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    policy_number: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    claim_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="processed")
    priority_level: Mapped[str] = mapped_column(String(16))
    priority_reason: Mapped[str] = mapped_column(Text)
    analyst_summary: Mapped[str] = mapped_column(Text)

    raw_claim: Mapped[dict] = mapped_column(JSON)
    structured_extraction: Mapped[dict] = mapped_column(JSON)
    missing_items: Mapped[list] = mapped_column(JSON)
    validation_flags: Mapped[list] = mapped_column(JSON)
    policy_context: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
