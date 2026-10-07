import time
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class RootCauseFamily(str, Enum):
    DATA_CORPUS = "DATA_CORPUS"
    TOKENIZER = "TOKENIZER"
    MODEL_ARCHITECTURE = "MODEL_ARCHITECTURE"
    CONTEXT_SYSTEM = "CONTEXT_SYSTEM"
    CHAT_TEMPLATE = "CHAT_TEMPLATE"
    INFERENCE_GENERATION = "INFERENCE_GENERATION"
    DECODING_TERMINATION = "DECODING_TERMINATION"
    TRAINING_RECIPE = "TRAINING_RECIPE"
    TRAINING_FAILURE = "TRAINING_FAILURE"
    CHECKPOINT_ARTIFACT = "CHECKPOINT_ARTIFACT"
    QUANTIZATION_PRECISION = "QUANTIZATION_PRECISION"
    RUNTIME = "RUNTIME"
    LLMFORGE_INTEGRATION = "LLMFORGE_INTEGRATION"
    HARDWARE_PERFORMANCE = "HARDWARE_PERFORMANCE"
    UNKNOWN = "UNKNOWN"

class HypothesisStatus(str, Enum):
    PROPOSED = "PROPOSED"
    SUPPORTED = "SUPPORTED"
    WEAKENED = "WEAKENED"
    FALSIFIED = "FALSIFIED"
    CONFIRMED = "CONFIRMED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

class HypothesisObject(BaseModel):
    hypothesis_id: str
    root_cause_family: RootCauseFamily
    root_cause: str
    supporting_evidence: List[str] = Field(default_factory=list)
    contradicting_evidence: List[str] = Field(default_factory=list)
    alternative_explanations: List[str] = Field(default_factory=list)
    confidence: float = 0.50 # Evidence score 0.0 to 1.0
    required_tests: List[str] = Field(default_factory=list)
    falsification_tests: List[str] = Field(default_factory=list)
    status: HypothesisStatus = HypothesisStatus.PROPOSED
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)

class CompetingHypothesesEngine:
    """Engine maintaining competing root-cause hypotheses with falsification-first testing logic."""

    def __init__(self):
        self.hypotheses: Dict[str, HypothesisObject] = {}

    def propose_hypothesis(
        self,
        hypothesis_id: str,
        family: RootCauseFamily,
        root_cause: str,
        supporting_evidence: List[str],
        confidence: float = 0.50
    ) -> HypothesisObject:
        hyp = HypothesisObject(
            hypothesis_id=hypothesis_id,
            root_cause_family=family,
            root_cause=root_cause,
            supporting_evidence=supporting_evidence,
            confidence=confidence,
            status=HypothesisStatus.PROPOSED
        )
        self.hypotheses[hypothesis_id] = hyp
        return hyp

    def apply_experiment_evidence(
        self,
        hypothesis_id: str,
        falsified: bool,
        evidence_note: str,
        new_confidence: float
    ) -> Optional[HypothesisObject]:
        hyp = self.hypotheses.get(hypothesis_id)
        if not hyp:
            return None

        hyp.updated_at = time.time()
        if falsified:
            hyp.status = HypothesisStatus.FALSIFIED
            hyp.confidence = 0.0
            hyp.contradicting_evidence.append(evidence_note)
        else:
            hyp.confidence = new_confidence
            if new_confidence >= 0.85:
                hyp.status = HypothesisStatus.CONFIRMED
            elif new_confidence > 0.50:
                hyp.status = HypothesisStatus.SUPPORTED
            else:
                hyp.status = HypothesisStatus.WEAKENED
            hyp.supporting_evidence.append(evidence_note)

        return hyp

    def get_ranked_hypotheses(self) -> List[HypothesisObject]:
        """Rank surviving hypotheses by confidence, excluding falsified ones."""
        surviving = [h for h in self.hypotheses.values() if h.status != HypothesisStatus.FALSIFIED]
        return sorted(surviving, key=lambda x: x.confidence, reverse=True)
