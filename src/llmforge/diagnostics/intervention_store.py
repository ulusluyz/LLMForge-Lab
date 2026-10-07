import os
import json
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class InterventionRecord(BaseModel):
    intervention_id: str
    run_id: str
    problem_summary: str
    primary_root_cause: str
    recommended_intervention: str
    human_decision: str = "DEFER" # ACCEPT, REJECT, MODIFY, DEFER
    human_notes: str = ""
    applied_status: str = "NOT_APPLIED" # NOT_APPLIED, APPLIED, SUCCESS, PARTIAL_SUCCESS, NO_EFFECT, REGRESSION, ROLLED_BACK
    model_version: str = "UNKNOWN"
    runtime_version: str = "UNKNOWN"
    timestamp: float = Field(default_factory=time.time)

class InterventionMemoryStore:
    """Persistent, provider-independent engineering memory store persisting intervention outcomes and human decisions."""

    def __init__(self, storage_dir: str):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self.memory_file = os.path.join(storage_dir, "intervention_engineering_memory.jsonl")

    def save_record(self, record: InterventionRecord) -> None:
        with open(self.memory_file, "a", encoding="utf-8") as f:
            f.write(record.model_dump_json() + "\n")

    def load_all_records(self) -> List[InterventionRecord]:
        if not os.path.exists(self.memory_file):
            return []
        records = []
        with open(self.memory_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(InterventionRecord.model_validate_json(line.strip()))
        return records

    def get_successful_interventions_for_cause(self, root_cause: str) -> List[InterventionRecord]:
        records = self.load_all_records()
        return [r for r in records if r.primary_root_cause == root_cause and r.applied_status == "SUCCESS"]
