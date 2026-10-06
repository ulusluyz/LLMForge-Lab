from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class TurnEvaluation(BaseModel):
    turn_index: int
    question_id: str
    observed_response: str
    extracted_signals: Dict[str, float] = Field(default_factory=dict) # e.g. {"context_retention": 0.8, "reasoning": 0.9}
    evidence: str
    counter_evidence: Optional[str] = None
    flaws_detected: List[str] = Field(default_factory=list)

class Hypothesis(BaseModel):
    hypothesis_id: str
    finding: str
    suspected_cause: str
    confidence: float
    evidence_nodes: List[str] = Field(default_factory=list)
    alternative_hypotheses: List[str] = Field(default_factory=list)

class RootCauseCandidate(BaseModel):
    category: str # MODEL_WEIGHTS, TOKENIZER, CONTEXT_WINDOW, INFERENCE_RUNTIME, PROMPT_TEMPLATE, DATA_EKSILIKGI, LLMFORGE_SYSTEM_ERROR
    description: str
    first_observed_turn: int
    confidence: float
    recommended_action: str
    reason_for_action: str

class DiagnosticReport(BaseModel):
    run_id: str
    total_turns: int
    metrics_summary: Dict[str, float] = Field(default_factory=dict)
    findings: List[str] = Field(default_factory=list)
    hypotheses: List[Hypothesis] = Field(default_factory=list)
    root_causes: List[RootCauseCandidate] = Field(default_factory=list)
