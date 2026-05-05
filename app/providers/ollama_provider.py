from __future__ import annotations

import json
import logging
import os
from typing import Optional

from ollama import Client
from ollama import RequestError, ResponseError

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


def _fallback_analyst_summary(payload: SummaryInput) -> str:
    """Short Spanish template when Ollama summarization fails."""
    ext = payload.structured_extraction
    pol = payload.policy_context
    missing = ", ".join(payload.missing_items) if payload.missing_items else "ninguno"
    flags = ", ".join(payload.validation_flags) if payload.validation_flags else "ninguna"
    pol_line = ""
    if pol:
        pol_line = (
            f"Póliza {pol.policy_number}: estado {pol.status}, "
            f"cobertura {'activa' if pol.coverage_active else 'inactiva o sin cobertura'}. "
        )
    next_action = (
        "Completar documentación faltante y validar cobertura operativa."
        if payload.missing_items or (pol and not pol.coverage_active)
        else "Continuar revisión según prioridad asignada."
    )
    damage = (ext.damage_description or "sin detalle operativo en extracción")[:200]
    return (
        "[Resumen automático — Ollama no disponible] "
        f"Siniestro {payload.claim_id}, prioridad {payload.priority.level}. "
        f"{pol_line}"
        f"Tipo siniestro: {ext.claim_type or '—'}. Daño / hecho: {damage}. "
        f"Pendientes: {missing}. Señales: {flags}. "
        f"Siguiente paso sugerido: {next_action}"
    )


class OllamaProvider(BaseLLMProvider):
    def __init__(self) -> None:
        self.client = Client(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
        self.model_extract = settings.ollama_model_extract
        self.model_summary = settings.ollama_model_summary

    def extract_claim(self, prompt: str) -> StructuredClaim:
        full_prompt = EXTRACTION_PROMPT + "\n\nClaim context:\n" + prompt
        try:
            response = self.client.generate(
                model=self.model_extract,
                prompt=full_prompt,
                format="json",
                stream=False,
            )
            # In Ollama, the response has a 'response' field with the actual text
            text = response.get("response", "")
            if not text:
                raise RuntimeError("Ollama did not return text for structured extraction.")
            try:
                return StructuredClaim.model_validate_json(text)
            except Exception as exc:
                logger.warning("Failed to parse Ollama structured output directly: %s", exc)
                # Try to extract JSON from the response if it's wrapped in text
                # Extract the JSON part from text that might have some surrounding text
                try:
                    # Look for JSON content between curly braces or square brackets
                    start_idx = text.find("{")
                    end_idx = text.rfind("}")
                    if start_idx == -1:
                        start_idx = text.find("[")
                        end_idx = text.rfind("]")
                    if start_idx != -1 and end_idx != -1:
                        json_text = text[start_idx:end_idx+1]
                        return StructuredClaim.model_validate_json(json_text)
                    else:
                        raise Exception("No JSON found in response")
                except Exception:
                    # Fallback to the original parsing
                    return StructuredClaim.model_validate(json.loads(text))
        except RequestError as exc:
            logger.error("Ollama request failed: %s", exc)
            raise RuntimeError(f"Ollama request failed: {exc}")
        except ResponseError as exc:
            logger.error("Ollama response error: %s", exc)
            raise RuntimeError(f"Ollama response error: {exc}")
        except Exception as exc:
            logger.error("Unexpected error in Ollama extraction: %s", exc)
            raise RuntimeError(f"Unexpected error in Ollama extraction: {exc}")

    def summarize_claim(self, payload: SummaryInput) -> str:
        payload_json = json.dumps(payload.model_dump(mode="json"), ensure_ascii=False, indent=2)
        try:
            response = self.client.generate(
                model=self.model_summary,
                prompt=SUMMARY_PROMPT_TEMPLATE.format(payload=payload_json),
                stream=False,
            )
            text = (response.get("response", "") or "").strip()
            return text or _fallback_analyst_summary(payload)
        except RequestError as exc:
            logger.error("Ollama request failed during summarization: %s", exc)
            raise RuntimeError(f"Ollama request failed during summarization: {exc}")
        except ResponseError as exc:
            logger.error("Ollama response error during summarization: %s", exc)
            raise RuntimeError(f"Ollama response error during summarization: {exc}")
        except Exception as exc:
            logger.error("Unexpected error in Ollama summarization: %s", exc)
            raise RuntimeError(f"Unexpected error in Ollama summarization: {exc}")