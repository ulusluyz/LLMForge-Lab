import os
import json
from typing import Dict, List, Any
from pydantic import BaseModel, Field

class AIHumanComparisonRecord(BaseModel):
    item_id: str
    provider_name: str
    ai_decision: str
    human_decision: str
    ai_labels: List[str] = Field(default_factory=list)
    human_labels: List[str] = Field(default_factory=list)
    decision_matches: bool
    label_overlap_count: int
    confidence: float = 0.85

class AIHumanAgreementTracker:
    """Tracks decision agreement, false accept/reject rates, and per-label precision/recall between AI recommendations and Human Ground Truth."""

    def __init__(self, storage_filepath: str = "data/ai_human_agreement.jsonl"):
        self.storage_filepath = storage_filepath
        os.makedirs(os.path.dirname(storage_filepath), exist_ok=True)

    def record_comparison(self, record: AIHumanComparisonRecord) -> None:
        with open(self.storage_filepath, "a", encoding="utf-8") as f:
            f.write(record.model_dump_json() + "\n")

    def load_records(self) -> List[AIHumanComparisonRecord]:
        if not os.path.exists(self.storage_filepath):
            return []
        records = []
        with open(self.storage_filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(AIHumanComparisonRecord.model_validate_json(line.strip()))
        return records

    def compute_metrics(self, provider_name: Optional[str] = None) -> Dict[str, Any]:
        records = self.load_records()
        if provider_name:
            records = [r for r in records if r.provider_name == provider_name]

        if not records:
            return {
                "total_comparisons": 0,
                "decision_agreement_rate": 0.0,
                "false_accept_rate": 0.0,
                "false_reject_rate": 0.0,
                "label_precision": 0.0,
                "label_recall": 0.0
            }

        total = len(records)
        matches = sum(1 for r in records if r.decision_matches)
        false_accepts = sum(1 for r in records if r.ai_decision == "ACCEPT" and r.human_decision == "REJECT")
        false_rejects = sum(1 for r in records if r.ai_decision == "REJECT" and r.human_decision == "ACCEPT")

        total_ai_labels = sum(len(r.ai_labels) for r in records)
        total_human_labels = sum(len(r.human_labels) for r in records)
        total_overlap = sum(r.label_overlap_count for r in records)

        precision = (total_overlap / total_ai_labels) if total_ai_labels > 0 else 1.0
        recall = (total_overlap / total_human_labels) if total_human_labels > 0 else 1.0

        return {
            "total_comparisons": total,
            "decision_agreement_rate": round(matches / total, 3),
            "false_accept_rate": round(false_accepts / total, 3),
            "false_reject_rate": round(false_rejects / total, 3),
            "label_precision": round(precision, 3),
            "label_recall": round(recall, 3)
        }
