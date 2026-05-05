from __future__ import annotations

from app.domain.schemas import SummaryInput
from app.providers.gemini_provider import GeminiProvider


class SummaryService:
    def __init__(self, provider: GeminiProvider | None = None) -> None:
        self.provider = provider or GeminiProvider()

    def summarize(self, payload: SummaryInput) -> str:
        return self.provider.summarize_claim(payload)
