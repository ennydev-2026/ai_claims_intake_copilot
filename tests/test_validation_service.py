from app.domain.schemas import StructuredClaim
from app.services.validation_service import ValidationService


def test_validation_detects_missing_policy_and_contact():
    service = ValidationService()
    claim = StructuredClaim(claim_type="auto", damage_description="Daño frontal")
    result = service.validate(claim)
    assert "numero_poliza" in result.missing_items
    assert "medio_contacto" in result.missing_items
