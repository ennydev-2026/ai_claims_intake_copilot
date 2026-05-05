from __future__ import annotations

import json
from pathlib import Path

from app.domain.schemas import InputClaim, SampleClaimInfo


class SampleService:
    def __init__(self) -> None:
        self.base_path = Path("datasets")

    def list_samples(self) -> list[SampleClaimInfo]:
        samples: list[SampleClaimInfo] = []
        for path in sorted(self.base_path.glob("claims_*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            samples.append(
                SampleClaimInfo(
                    sample_name=path.name,
                    claim_id=data["claim_id"],
                    claim_type=data.get("claim_type"),
                    policy_number=data.get("policy_number"),
                    subject=data.get("subject"),
                )
            )
        return samples

    def get_sample(self, sample_name: str) -> InputClaim:
        path = self.base_path / sample_name
        if not path.exists():
            raise FileNotFoundError(sample_name)
        return InputClaim.model_validate(json.loads(path.read_text(encoding="utf-8")))
