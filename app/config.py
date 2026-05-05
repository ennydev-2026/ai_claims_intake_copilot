from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "local")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    app_name: str = os.getenv("APP_NAME", "AI Claims Intake Copilot")
    app_version: str = os.getenv("APP_VERSION", "0.2.0")

    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model_extract: str = os.getenv("GEMINI_MODEL_EXTRACT", "gemini-2.5-flash")
    gemini_model_summary: str = os.getenv("GEMINI_MODEL_SUMMARY", "gemini-2.5-flash")

    database_url: str = os.getenv("DATABASE_URL", "sqlite+pysqlite:///./claims.db")
    mock_java_base_url: str = os.getenv("MOCK_JAVA_BASE_URL", "http://localhost:8081")
    dashboard_api_base_url: str = os.getenv("DASHBOARD_API_BASE_URL", "http://localhost:8000")

    enable_policy_enrichment: bool = os.getenv("ENABLE_POLICY_ENRICHMENT", "true").lower() == "true"
    enable_java_callback: bool = os.getenv("ENABLE_JAVA_CALLBACK", "true").lower() == "true"


settings = Settings()
