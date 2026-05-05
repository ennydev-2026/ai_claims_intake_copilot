from __future__ import annotations

import json
from pathlib import Path

import httpx

sample_path = Path("datasets/claims_001.json")
payload = json.loads(sample_path.read_text(encoding="utf-8"))

response = httpx.post("http://localhost:8000/api/v1/claims/intake", json=payload, timeout=60.0)
print(response.status_code)
print(response.json())
