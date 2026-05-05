# AI Claims Intake Copilot - Ollama Integration Plan

## 1. OBJECTIVE

Implement support for local Ollama inference in the AI Claims Intake Copilot, allowing the application to work with local LLM models while retaining the current Google Gemini functionality as a fallback.

## 2. CONTEXT SUMMARY

This is a FastAPI application for insurance claims intake that currently uses Google's Gemini API for structured extraction and summarization. The codebase follows a provider pattern with:
- `app/providers/gemini_provider.py` - Currently handles Gemini API interactions
- `app/providers/base.py` - Defines the interface for LLM providers
- `app/services/extraction_service.py` and `summary_service.py` - Use providers via dependency injection
- `app/config.py` - Configuration loading for API keys and model settings

## 3. APPROACH OVERVIEW

The approach will involve:
1. Creating an `OllamaProvider` class that implements the same interface as `GeminiProvider`
2. Implementing auto-detection logic to use Ollama when available, fallback to Gemini otherwise
3. Updating configuration to support Ollama settings
4. Modifying dependency injection to use the appropriate provider
5. Updating documentation with instructions for Ollama setup

## 4. IMPLEMENTATION STEPS

1. **Create Ollama Provider Implementation**
   - Create `app/providers/ollama_provider.py` implementing `OllamaProvider` class
   - Use `ollama` Python client for local LLM interaction
   - Match the same method signatures as `GeminiProvider`
   - Add proper error handling and fallback behavior

2. **Modify Provider Selection Logic**
   - Update service classes (`extraction_service.py` and `summary_service.py`) to support auto-detection of Ollama
   - Modify service constructors to accept optional provider instances
   - Implement automatic fallback from Ollama to Gemini when Ollama is not available
   - Update dependency injection to use appropriate provider based on availability

3. **Update Configuration System**
   - Add Ollama-specific environment variables in `app/config.py`
   - Implement auto-detection logic for Ollama service availability
   - Add default model settings for Ollama models
   - Allow Ollama to be activated by setting `OLLAMA_ENABLED=true` in environment

4. **Update Documentation**
   - Modify README to document Ollama setup instructions
   - Add environment variable examples for Ollama
   - Include information about how to pull and run models locally

## 5. TESTING AND VALIDATION

- Verify that Ollama provider works with local models
- Confirm that the application falls back to Gemini when Ollama is unavailable
- Validate that all API routes function correctly with both providers
- Test with sample claims to ensure accurate processing
