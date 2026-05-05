from __future__ import annotations

import logging

import httpx

from app.config import settings
from app.domain.schemas import PolicyContext

logger = logging.getLogger(__name__)


class PolicyService:
    def __init__(self) -> None:
        self.base_url = settings.mock_java_base_url.rstrip("/")

    def fetch_policy(self, policy_number: str | None) -> PolicyContext | None:
        if not settings.enable_policy_enrichment or not policy_number:
            return None

        url = f"{self.base_url}/api/policies/{policy_number}"
        try:
            response = httpx.get(url, timeout=5.0)
            response.raise_for_status()
            return PolicyContext.model_validate(response.json())
        except Exception as exc:  # pragma: no cover - network resilience
            logger.warning("Could not fetch policy context from mock Java service: %s", exc)
            return None

    def publish_intake_event(self, payload: dict) -> None:
        if not settings.enable_java_callback:
            return
        url = f"{self.base_url}/api/claims/intake-events"
        try:
            response = httpx.post(url, json=payload, timeout=5.0)
            response.raise_for_status()
        except Exception as exc:  # pragma: no cover - network resilience
            logger.warning("Could not publish intake event to mock Java service: %s", exc)
