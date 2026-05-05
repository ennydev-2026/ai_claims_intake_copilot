from __future__ import annotations

from app.domain.schemas import PolicyContext, PriorityResult, StructuredClaim, ValidationResult


class PriorityService:
    def classify(self, claim: StructuredClaim, validation: ValidationResult, policy_context: PolicyContext | None = None) -> PriorityResult:
        urgency = " ".join(claim.urgency_signals).lower()
        incident_type = (claim.incident_type or "").lower()
        claim_type = (claim.claim_type or "").lower()
        damage = (claim.damage_description or "").lower()

        if (
            claim.injuries_reported
            or claim.third_party_involved
            or claim_type == "incendio"
            or "fire" in incident_type
            or "robo_total" in incident_type
            or "total theft" in incident_type
            or "lesion" in urgency
            or "urgente" in urgency
            or "inmovilizado" in urgency
        ):
            return PriorityResult(
                level="alta",
                reason="El caso presenta señales de severidad alta o posible impacto legal/operativo inmediato.",
            )

        if policy_context and not policy_context.coverage_active:
            return PriorityResult(
                level="media",
                reason="La póliza aparece inactiva o sin cobertura, por lo que el caso requiere validación operativa.",
            )

        if damage or validation.missing_items or "collision" in incident_type or "water" in incident_type or "robo" in incident_type:
            return PriorityResult(
                level="media",
                reason="Hay daño material, ambigüedad operativa o documentación incompleta que requiere revisión.",
            )

        return PriorityResult(
            level="baja",
            reason="No se observan señales de criticidad inmediata y el caso parece preliminar o de baja severidad.",
        )
