import random
import os
import json
from typing import List, Dict, Any
from pydantic import BaseModel, Field

class ShadowAuditSample(BaseModel):
    sample_id: str
    item_id: str
    auto_decision: str
    assigned_labels: List[str] = Field(default_factory=list)
    human_shadow_decision: Optional[str] = None
    disagreement: bool = False

class ShadowAuditSampler:
    """Samples auto-decided records for periodic human shadow audits to detect automation policy drift."""

    def __init__(self, sample_rate: float = 0.05, storage_filepath: str = "data/shadow_audit_samples.jsonl"):
        self.sample_rate = sample_rate
        self.storage_filepath = storage_filepath
        os.makedirs(os.path.dirname(storage_filepath), exist_ok=True)

    def should_sample(self) -> bool:
        return random.random() < self.sample_rate

    def record_sample(self, item_id: str, auto_decision: str, labels: List[str]) -> ShadowAuditSample:
        sample = ShadowAuditSample(
            sample_id=f"shd_{item_id}",
            item_id=item_id,
            auto_decision=auto_decision,
            assigned_labels=labels
        )
        with open(self.storage_filepath, "a", encoding="utf-8") as f:
            f.write(sample.model_dump_json() + "\n")
        return sample

    def load_samples(self) -> List[ShadowAuditSample]:
        if not os.path.exists(self.storage_filepath):
            return []
        samples = []
        with open(self.storage_filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    samples.append(ShadowAuditSample.model_validate_json(line.strip()))
        return samples

    def get_disagreement_rate(self) -> float:
        samples = [s for s in self.load_samples() if s.human_shadow_decision is not None]
        if not samples:
            return 0.0
        disagreements = sum(1 for s in samples if s.disagreement)
        return round(disagreements / len(samples), 3)
