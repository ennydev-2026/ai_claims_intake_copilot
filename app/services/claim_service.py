from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.domain.schemas import ExtractResponse, InputClaim, IntakeMetadata, IntakeResponse, PriorityResult, StructuredClaim, SummaryInput, ValidationResult
from app.services.extraction_service import ExtractionService
from app.services.policy_service import PolicyService
from app.services.priority_service import PriorityService
from app.services.repository_service import RepositoryService
from app.services.summary_service import SummaryService
from app.services.validation_service import ValidationService


class ClaimService:
    def __init__(self) -> None:
        self.extraction_service = ExtractionService()
        self.validation_service = ValidationService()
        self.priority_service = PriorityService()
        self.summary_service = SummaryService()
        self.policy_service = PolicyService()
        self.repository_service = RepositoryService()

    def extract_only(self, claim: InputClaim) -> ExtractResponse:
        policy_context = self.policy_service.fetch_policy(claim.policy_number)
        extracted = self.extraction_service.extract(claim, policy_context)
        return ExtractResponse(claim_id=claim.claim_id, policy_context=policy_context, structured_extraction=extracted)

    def validate_only(self, structured_claim: StructuredClaim) -> ValidationResult:
        return self.validation_service.validate(structured_claim)

    def summarize_only(
        self,
        claim_id: str,
        original_claim: dict,
        structured_claim: StructuredClaim,
        validation: ValidationResult,
        priority: PriorityResult,
    ) -> str:
        payload = SummaryInput(
            claim_id=claim_id,
            original_claim=original_claim,
            structured_extraction=structured_claim,
            missing_items=validation.missing_items,
            validation_flags=validation.validation_flags,
            priority=priority,
        )
        return self.summary_service.summarize(payload)

    def process(self, claim: InputClaim, db: Session) -> IntakeResponse:
        policy_context = self.policy_service.fetch_policy(claim.policy_number)
        extracted = self.extraction_service.extract(claim, policy_context)
        validation = self.validation_service.validate(extracted, policy_context)
        priority = self.priority_service.classify(extracted, validation, policy_context)
        summary = self.summary_service.summarize(
            SummaryInput(
                claim_id=claim.claim_id,
                original_claim=claim.model_dump(mode="json"),
                structured_extraction=extracted,
                missing_items=validation.missing_items,
                validation_flags=validation.validation_flags,
                priority=priority,
                policy_context=policy_context,
            )
        )
        response = IntakeResponse(
            claim_id=claim.claim_id,
            policy_context=policy_context,
            structured_extraction=extracted,
            missing_items=validation.missing_items,
            validation_flags=validation.validation_flags,
            priority=priority,
            analyst_summary=summary,
            metadata=IntakeMetadata(provider="gemini", pipeline_version="v2", processed_at=datetime.now(timezone.utc)),
        )
        record = self.repository_service.save_intake(db, response, claim.model_dump(mode="json"))
        response.db_id = record.id
        self.policy_service.publish_intake_event({
            "claim_id": response.claim_id,
            "db_id": response.db_id,
            "priority": response.priority.level,
            "policy_number": response.structured_extraction.policy_number,
            "status": response.status,
        })
        return response
