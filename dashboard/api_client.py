from __future__ import annotations

import os

import httpx

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")


def api_get(path: str):
    response = httpx.get(f"{API_BASE_URL}{path}", timeout=20.0)
    response.raise_for_status()
    return response.json()


def api_post(path: str, payload: dict | None = None):
    response = httpx.post(f"{API_BASE_URL}{path}", json=payload, timeout=60.0)
    response.raise_for_status()
    return response.json()
