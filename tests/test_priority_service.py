from app.domain.schemas import StructuredClaim, ValidationResult
from app.services.priority_service import PriorityService


def test_priority_high_for_injuries():
    service = PriorityService()
    claim = StructuredClaim(
        claim_type="auto",
        incident_type="auto_collision",
        damage_description="Daño frontal",
        injuries_reported=True,
    )
    result = service.classify(claim, ValidationResult())
    assert result.level == "alta"
