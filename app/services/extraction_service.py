from __future__ import annotations

import logging

from app.domain.schemas import InputClaim, PolicyContext, StructuredClaim
from app.providers.gemini_provider import GeminiProvider

logger = logging.getLogger(__name__)


def _fallback_structured_claim(claim: InputClaim, policy_context: PolicyContext | None = None) -> StructuredClaim:
    """Deterministic extraction when Gemini is unavailable (e.g. quota)."""
    ctype = claim.claim_type or (policy_context.product_line if policy_context else None)
    damage = (claim.message or "").strip() or (claim.subject or "").strip() or None
    docs = ["photos"] if claim.attachments else []
    return StructuredClaim(
        policy_number=claim.policy_number,
        claim_type=ctype,
        incident_date=claim.incident_date,
        report_date=claim.reported_at.date() if claim.reported_at else None,
        damage_description=damage,
        documents_detected=docs,
        customer_contact_present=bool(claim.contact.email or claim.contact.phone),
        contact_email=claim.contact.email,
        contact_phone=claim.contact.phone,
    )


class ExtractionService:
    def __init__(self, provider: GeminiProvider | None = None) -> None:
        self.provider = provider or GeminiProvider()

    def build_prompt(self, claim: InputClaim, policy_context: PolicyContext | None = None) -> str:
        attachments = ", ".join(claim.attachments) if claim.attachments else "none"
        policy_block = (
            f"- policy_status: {policy_context.status}\n"
            f"- policy_coverage_active: {policy_context.coverage_active}\n"
            f"- policy_product_line: {policy_context.product_line}\n"
            if policy_context else
            "- policy_status: unknown\n- policy_coverage_active: unknown\n- policy_product_line: unknown\n"
        )
        return (
            f"- claim_id: {claim.claim_id}\n"
            f"- channel: {claim.channel}\n"
            f"- customer_name: {claim.customer_name}\n"
            f"- explicit_policy_number: {claim.policy_number}\n"
            f"- explicit_claim_type: {claim.claim_type}\n"
            f"- incident_date: {claim.incident_date}\n"
            f"- reported_at: {claim.reported_at}\n"
            f"- subject: {claim.subject}\n"
            f"- message: {claim.message}\n"
            f"- attachments: {attachments}\n"
            f"- contact_email: {claim.contact.email}\n"
            f"- contact_phone: {claim.contact.phone}\n"
            f"{policy_block}"
        )

    def extract(self, claim: InputClaim, policy_context: PolicyContext | None = None) -> StructuredClaim:
        try:
            extracted = self.provider.extract_claim(self.build_prompt(claim, policy_context))
        except Exception as exc:
            logger.warning(
                "Gemini extraction failed (%s); using heuristic fallback: %s",
                type(exc).__name__,
                exc,
            )
            extracted = _fallback_structured_claim(claim, policy_context)
        if not extracted.policy_number:
            extracted.policy_number = claim.policy_number
        if not extracted.claim_type:
            extracted.claim_type = claim.claim_type or getattr(policy_context, "product_line", None)
        if not extracted.incident_date:
            extracted.incident_date = claim.incident_date
        if claim.reported_at and not extracted.report_date:
            extracted.report_date = claim.reported_at.date()
        if claim.contact.email and not extracted.contact_email:
            extracted.contact_email = claim.contact.email
        if claim.contact.phone and not extracted.contact_phone:
            extracted.contact_phone = claim.contact.phone
        if extracted.customer_contact_present is None:
            extracted.customer_contact_present = bool(extracted.contact_email or extracted.contact_phone)
        if claim.attachments and not extracted.documents_detected:
            extracted.documents_detected = ["photos"]
        return extracted
