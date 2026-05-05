from __future__ import annotations

from abc import ABC, abstractmethod
from app.domain.schemas import StructuredClaim, SummaryInput


class BaseLLMProvider(ABC):
    @abstractmethod
    def extract_claim(self, prompt: str) -> StructuredClaim:
        raise NotImplementedError

    @abstractmethod
    def summarize_claim(self, payload: SummaryInput) -> str:
        raise NotImplementedError
