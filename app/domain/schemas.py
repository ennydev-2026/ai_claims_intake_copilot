from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

PriorityLevel = Literal["alta", "media", "baja"]


class ContactInfo(BaseModel):
    email: str | None = None
    phone: str | None = None


class PolicyContext(BaseModel):
    policy_number: str
    status: str
    coverage_active: bool
    product_line: str | None = None
    customer_segment: str | None = None
    sum_insured: float | None = None
    currency: str | None = None

    model_config = ConfigDict(extra="ignore")


class InputClaim(BaseModel):
    claim_id: str
    channel: str = "email"
    customer_name: str | None = None
    policy_number: str | None = None
    claim_type: str | None = None
    incident_date: date | None = None
    reported_at: datetime | None = None
    subject: str | None = None
    message: str
    attachments: list[str] = Field(default_factory=list)
    contact: ContactInfo = Field(default_factory=ContactInfo)


class StructuredClaim(BaseModel):
    policy_number: str | None = None
    claim_type: str | None = None
    incident_type: str | None = None
    incident_date: date | None = None
    report_date: date | None = None
    location: str | None = None
    damage_description: str | None = None
    injuries_reported: bool | None = None
    third_party_involved: bool | None = None
    urgency_signals: list[str] = Field(default_factory=list)
    documents_detected: list[str] = Field(default_factory=list)
    customer_contact_present: bool | None = None
    contact_email: str | None = None
    contact_phone: str | None = None

    model_config = ConfigDict(extra="ignore")


class ValidationResult(BaseModel):
    missing_items: list[str] = Field(default_factory=list)
    validation_flags: list[str] = Field(default_factory=list)


class PriorityResult(BaseModel):
    level: PriorityLevel
    reason: str


class IntakeMetadata(BaseModel):
    provider: str = "gemini"
    pipeline_version: str = "v2"
    processed_at: datetime


class IntakeResponse(BaseModel):
    db_id: int | None = None
    claim_id: str
    status: str = "processed"
    policy_context: PolicyContext | None = None
    structured_extraction: StructuredClaim
    missing_items: list[str]
    validation_flags: list[str]
    priority: PriorityResult
    analyst_summary: str
    metadata: IntakeMetadata


class ExtractResponse(BaseModel):
    claim_id: str
    policy_context: PolicyContext | None = None
    structured_extraction: StructuredClaim


class SummaryInput(BaseModel):
    claim_id: str
    original_claim: dict[str, Any]
    structured_extraction: StructuredClaim
    missing_items: list[str] = Field(default_factory=list)
    validation_flags: list[str] = Field(default_factory=list)
    priority: PriorityResult
    policy_context: PolicyContext | None = None


class ClaimRecordView(BaseModel):
    id: int
    claim_id: str
    customer_name: str | None = None
    policy_number: str | None = None
    claim_type: str | None = None
    status: str
    priority_level: str
    priority_reason: str
    analyst_summary: str
    missing_items: list[str]
    validation_flags: list[str]
    raw_claim: dict[str, Any]
    structured_extraction: dict[str, Any]
    policy_context: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DashboardSummary(BaseModel):
    total_claims: int
    alta: int
    media: int
    baja: int


class SampleClaimInfo(BaseModel):
    sample_name: str
    claim_id: str
    claim_type: str | None = None
    policy_number: str | None = None
    subject: str | None = None
