from __future__ import annotations

from collections import Counter

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.domain.schemas import ClaimRecordView, DashboardSummary, IntakeResponse
from app.models.claim_record import ClaimRecord


class RepositoryService:
    def save_intake(self, db: Session, response: IntakeResponse, raw_claim: dict) -> ClaimRecord:
        existing = db.scalar(select(ClaimRecord).where(ClaimRecord.claim_id == response.claim_id))
        if existing:
            existing.customer_name = raw_claim.get("customer_name")
            existing.policy_number = raw_claim.get("policy_number")
            existing.claim_type = raw_claim.get("claim_type")
            existing.status = response.status
            existing.priority_level = response.priority.level
            existing.priority_reason = response.priority.reason
            existing.analyst_summary = response.analyst_summary
            existing.raw_claim = raw_claim
            existing.structured_extraction = response.structured_extraction.model_dump(mode="json")
            existing.missing_items = response.missing_items
            existing.validation_flags = response.validation_flags
            existing.policy_context = response.policy_context.model_dump(mode="json") if response.policy_context else None
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing

        record = ClaimRecord(
            claim_id=response.claim_id,
            customer_name=raw_claim.get("customer_name"),
            policy_number=raw_claim.get("policy_number"),
            claim_type=raw_claim.get("claim_type"),
            status=response.status,
            priority_level=response.priority.level,
            priority_reason=response.priority.reason,
            analyst_summary=response.analyst_summary,
            raw_claim=raw_claim,
            structured_extraction=response.structured_extraction.model_dump(mode="json"),
            missing_items=response.missing_items,
            validation_flags=response.validation_flags,
            policy_context=response.policy_context.model_dump(mode="json") if response.policy_context else None,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def recent_claims(self, db: Session, limit: int = 20) -> list[ClaimRecordView]:
        records = db.scalars(select(ClaimRecord).order_by(desc(ClaimRecord.created_at)).limit(limit)).all()
        return [ClaimRecordView.model_validate(record) for record in records]

    def get_claim(self, db: Session, claim_id: str) -> ClaimRecordView | None:
        record = db.scalar(select(ClaimRecord).where(ClaimRecord.claim_id == claim_id))
        return ClaimRecordView.model_validate(record) if record else None

    def dashboard_summary(self, db: Session) -> DashboardSummary:
        total = db.scalar(select(func.count()).select_from(ClaimRecord)) or 0
        counts = Counter(
            db.scalars(select(ClaimRecord.priority_level)).all()
        )
        return DashboardSummary(
            total_claims=total,
            alta=counts.get("alta", 0),
            media=counts.get("media", 0),
            baja=counts.get("baja", 0),
        )
