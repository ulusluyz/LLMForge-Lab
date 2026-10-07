import os
import json
import time
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field

class PassageAnnotation(BaseModel):
    passage_id: str
    start_offset: int
    end_offset: int
    selected_text: str
    labels: List[str] = Field(default_factory=list)
    reason: str = ""

class HumanReviewRecord(BaseModel):
    review_id: str
    document_id: str
    document_text: str
    decision: str # ACCEPT, REJECT, HUMAN_REVIEW, REVIEW_LATER
    labels: List[str] = Field(default_factory=list)
    passage_annotations: List[PassageAnnotation] = Field(default_factory=list)
    reviewer_note: str = ""
    reason: str = ""
    source_url: str = ""
    provenance: str = "UNKNOWN"
    license_status: str = "UNKNOWN"
    timestamp: float = Field(default_factory=time.time)
    policy_version: str = "1.0.0"
    is_correction: bool = False # High-value learning event flag
    correction_type: Optional[str] = None # FALSE_POSITIVE, FALSE_NEGATIVE
    provider_recommendation: Optional[str] = None
    system_recommendation: Optional[str] = None

class HumanFeedbackStore:
    """Persistent, provider-independent Human Review Store supporting passage-level annotations and multi-label assignments."""

    def __init__(self, storage_dir: str):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self.evidence_file = os.path.join(storage_dir, "human_feedback_evidence.jsonl")

    def save_record(self, record: HumanReviewRecord) -> None:
        with open(self.evidence_file, "a", encoding="utf-8") as f:
            f.write(record.model_dump_json() + "\n")

    def load_all_records(self) -> List[HumanReviewRecord]:
        if not os.path.exists(self.evidence_file):
            return []
        records = []
        with open(self.evidence_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(HumanReviewRecord.model_validate_json(line.strip()))
        return records

    def export_backup(self, backup_filepath: str) -> None:
        records = self.load_all_records()
        with open(backup_filepath, "w", encoding="utf-8") as f:
            for r in records:
                f.write(r.model_dump_json() + "\n")

    def import_backup(self, backup_filepath: str) -> int:
        if not os.path.exists(backup_filepath):
            return 0
        imported_count = 0
        with open(backup_filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rec = HumanReviewRecord.model_validate_json(line.strip())
                    self.save_record(rec)
                    imported_count += 1
        return imported_count
