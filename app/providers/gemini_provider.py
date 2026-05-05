from __future__ import annotations

import json
import logging

from google import genai

from app.config import settings
from app.domain.schemas import StructuredClaim, SummaryInput
from app.providers.base import BaseLLMProvider

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """You are an insurance claims intake extraction engine.

Your task is to extract structured information from a synthetic insurance claim intake.
Only return the fields requested.
If a field is not present, return null.
Do not infer facts that are not explicitly present.
Normalize dates when possible.
Documents detected should be a short list like ["photos", "police_report"] when applicable.

Return valid JSON only.
"""

SUMMARY_PROMPT_TEMPLATE = """You are an insurance claims analyst copilot.

You will receive:
1) original claim data
2) optional policy context from a core insurance platform
3) structured extraction
4) missing items
5) validation flags
6) assigned priority

Write a short analyst-ready summary in Spanish.
Be factual, concise, and operational.
Do not speculate.
Mention the next suggested action.
Maximum length: 120 words.

Payload:
{payload}
"""


class GeminiProvider(BaseLLMProvider):
    def __init__(self) -> None:
        if not settings.gemini_api_key or settings.gemini_api_key == "REPLACE_WITH_YOUR_GEMINI_API_KEY":
            raise ValueError("GEMINI_API_KEY is missing. Set it in .env before running the API.")
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model_extract = settings.gemini_model_extract
        self.model_summary = settings.gemini_model_summary

    def extract_claim(self, prompt: str) -> StructuredClaim:
        full_prompt = EXTRACTION_PROMPT + "\n\nClaim context:\n" + prompt
        response = self.client.models.generate_content(
            model=self.model_extract,
            contents=full_prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": StructuredClaim.model_json_schema(),
            },
        )
        text = getattr(response, "text", None)
        if not text:
            raise RuntimeError("Gemini did not return text for structured extraction.")
        try:
            return StructuredClaim.model_validate_json(text)
        except Exception as exc:
            logger.warning("Failed to parse Gemini structured output directly: %s", exc)
            return StructuredClaim.model_validate(json.loads(text))

    def summarize_claim(self, payload: SummaryInput) -> str:
        payload_json = json.dumps(payload.model_dump(mode="json"), ensure_ascii=False, indent=2)
        response = self.client.models.generate_content(
            model=self.model_summary,
            contents=SUMMARY_PROMPT_TEMPLATE.format(payload=payload_json),
        )
        text = (getattr(response, "text", "") or "").strip()
        return text or "No fue posible generar el resumen para el analista."
