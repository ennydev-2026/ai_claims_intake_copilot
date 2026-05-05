from __future__ import annotations

import logging

from app.domain.schemas import SummaryInput
from app.providers.gemini_provider import GeminiProvider
from app.providers.ollama_provider import OllamaProvider
from app.config import settings

logger = logging.getLogger(__name__)


class SummaryService:
    def __init__(self, provider: GeminiProvider | OllamaProvider | None = None) -> None:
        if provider is not None:
            self.provider = provider
        elif settings.ollama_enabled:
            # Try to use Ollama first if enabled
            try:
                self.provider = OllamaProvider()
                # Test if Ollama is actually accessible
                test_response = self.provider.summarize_claim(SummaryInput(
                    claim_id="test",
                    structured_extraction=None,
                    policy_context=None,
                    missing_items=[],
                    validation_flags=[],
                    priority=None
                ))
                logger.info("Successfully initialized Ollama provider")
            except Exception:
                logger.warning("Ollama not accessible, falling back to Gemini")
                self.provider = GeminiProvider()
        else:
            # Default to Gemini when Ollama is not enabled
            self.provider = GeminiProvider()

    def summarize(self, payload: SummaryInput) -> str:
        return self.provider.summarize_claim(payload)
