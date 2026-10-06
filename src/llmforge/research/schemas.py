from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class DataRequirementSpec(BaseModel):
    requirement_id: str
    language: str = "tr"
    domain: str = "general_knowledge"
    content_style: str = "dialogue_and_reasoning"
    target_token_count: int = 100000
    multi_turn: bool = True
    min_turns: int = 5
    reasoning_required: bool = True
    context_dependency: bool = True
    targeted_diagnostic_root_cause: str
    justification: str

class SourceAuditRecord(BaseModel):
    source_id: str
    source_url: str
    source_type: str = "web_dataset"
    provenance: str = "UNKNOWN"
    license_status: str = "UNKNOWN"
    language: str = "tr"
    quality_signal_score: float = 0.0
    diagnostic_relevance_score: float = 0.0
    duplicate_risk: float = 0.0
    synthetic_risk: float = 0.0
    decision: str = "HUMAN_REVIEW" # ACCEPT, HUMAN_REVIEW, REJECT
    decision_reason: str = ""
