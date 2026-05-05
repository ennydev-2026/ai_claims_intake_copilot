from __future__ import annotations

from app.domain.schemas import PolicyContext, StructuredClaim, ValidationResult


class ValidationService:
    REQUIRED_BY_TYPE = {
        "auto": ["policy_number", "incident_date", "damage_description", "contact", "photos"],
        "robo": ["policy_number", "incident_date", "damage_description", "contact", "police_report_or_mention"],
        "incendio": ["policy_number", "incident_date", "damage_description", "contact"],
        "hogar": ["policy_number", "incident_date", "damage_description", "contact"],
    }

    def validate(self, claim: StructuredClaim, policy_context: PolicyContext | None = None) -> ValidationResult:
        missing_items: list[str] = []
        flags: list[str] = []
        claim_type = (claim.claim_type or "").lower().strip()

        if not claim.policy_number:
            missing_items.append("numero_poliza")
            flags.append("missing_policy_number")
        if not claim.incident_date:
            missing_items.append("fecha_incidente")
        if not claim.damage_description:
            missing_items.append("descripcion_dano")
        if not (claim.contact_email or claim.contact_phone or claim.customer_contact_present):
            missing_items.append("medio_contacto")
            flags.append("no_contact_provided")
        elif not claim.contact_phone:
            flags.append("missing_contact_phone")

        docs = {doc.lower() for doc in claim.documents_detected}
        required = self.REQUIRED_BY_TYPE.get(claim_type, [])
        if "photos" in required and "photos" not in docs:
            missing_items.append("evidencia_fotografica")
            flags.append("damage_but_no_evidence")
        if "police_report_or_mention" in required and "police_report" not in docs:
            missing_items.append("denuncia_o_constancia")
        if claim.incident_date and claim.report_date and claim.incident_date > claim.report_date:
            flags.append("incident_date_after_report_date")

        urgency_text = " ".join(claim.urgency_signals).lower()
        if any(word in urgency_text for word in ["urgente", "total", "lesion", "incendio"]) and not claim.damage_description:
            flags.append("high_urgency_without_details")

        if policy_context:
            if not policy_context.coverage_active:
                flags.append("inactive_or_no_coverage_policy")
            if policy_context.status.lower() not in {"active", "vigente"}:
                flags.append("policy_status_not_active")

        return ValidationResult(
            missing_items=list(dict.fromkeys(missing_items)),
            validation_flags=list(dict.fromkeys(flags)),
        )
