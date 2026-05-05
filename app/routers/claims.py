from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.domain.schemas import DashboardSummary, ExtractResponse, InputClaim, IntakeResponse, PriorityResult, StructuredClaim, SummaryInput, ValidationResult
from app.services.claim_service import ClaimService
from app.services.priority_service import PriorityService
from app.services.repository_service import RepositoryService
from app.services.sample_service import SampleService
from app.services.summary_service import SummaryService
from app.services.validation_service import ValidationService

router = APIRouter()
claim_service = ClaimService()
validation_service = ValidationService()
priority_service = PriorityService()
summary_service = SummaryService()
repository_service = RepositoryService()
sample_service = SampleService()


@router.post('/intake', response_model=IntakeResponse)
def intake_claim(payload: InputClaim, db: Session = Depends(get_db)) -> IntakeResponse:
    return claim_service.process(payload, db)


@router.post('/extract', response_model=ExtractResponse)
def extract_claim(payload: InputClaim) -> ExtractResponse:
    return claim_service.extract_only(payload)


@router.post('/validate', response_model=ValidationResult)
def validate_claim(payload: StructuredClaim) -> ValidationResult:
    return validation_service.validate(payload)


@router.post('/priority', response_model=PriorityResult)
def priority_claim(payload: StructuredClaim) -> PriorityResult:
    validation = validation_service.validate(payload)
    return priority_service.classify(payload, validation)


@router.post('/summarize')
def summarize_claim(payload: SummaryInput) -> dict[str, str]:
    return {'analyst_summary': summary_service.summarize(payload)}


@router.get('/recent')
def recent_claims(limit: int = Query(default=20, le=100), db: Session = Depends(get_db)) -> list[dict]:
    return [item.model_dump(mode="json") for item in repository_service.recent_claims(db, limit)]


@router.get('/dashboard/summary', response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db)) -> DashboardSummary:
    return repository_service.dashboard_summary(db)


@router.get('/samples')
def list_samples() -> list[dict]:
    return [item.model_dump(mode="json") for item in sample_service.list_samples()]


@router.get('/samples/{sample_name}')
def get_sample(sample_name: str) -> dict:
    try:
        sample = sample_service.get_sample(sample_name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Sample not found")
    return sample.model_dump(mode="json")


@router.post('/samples/{sample_name}/run', response_model=IntakeResponse)
def run_sample(sample_name: str, db: Session = Depends(get_db)) -> IntakeResponse:
    try:
        sample = sample_service.get_sample(sample_name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Sample not found")
    return claim_service.process(sample, db)


@router.get('/{claim_id}')
def get_claim(claim_id: str, db: Session = Depends(get_db)) -> dict:
    item = repository_service.get_claim(db, claim_id)
    if not item:
        raise HTTPException(status_code=404, detail="Claim not found")
    return item.model_dump(mode="json")
