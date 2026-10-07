import os
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from llmforge.review.store import HumanReviewRecord
from llmforge.review.learning import ThreeLayerLearningEngine, DecisionResult

class AutonomyMode(str):
    MANUAL = "MANUAL"
    SHADOW = "SHADOW"
    ASSISTED = "ASSISTED"
    AUTONOMOUS = "AUTONOMOUS"

class PromotionGateResult(BaseModel):
    promoted: bool
    current_accuracy: float
    candidate_accuracy: float
    reason: str
    label_regressions: List[str] = Field(default_factory=list)

class PromotionGate:
    """Promotion Gate enforcing Golden Validation set benchmarking and per-label regression checks before policy promotion."""

    def __init__(self, golden_set: List[HumanReviewRecord]):
        self.golden_set = golden_set

    def evaluate_candidate_policy(
        self,
        current_engine: ThreeLayerLearningEngine,
        candidate_engine: ThreeLayerLearningEngine,
        min_accuracy_threshold: float = 0.85
    ) -> PromotionGateResult:
        if not self.golden_set:
            return PromotionGateResult(
                promoted=True,
                current_accuracy=1.0,
                candidate_accuracy=1.0,
                reason="Golden validation set is empty; auto-promoted candidate policy."
            )

        # Benchmark candidate policy against Golden Validation Set
        correct_current = 0
        correct_candidate = 0
        regressions = []

        for rec in self.golden_set:
            curr_res = current_engine.evaluate_document(rec.document_text)
            cand_res = candidate_engine.evaluate_document(rec.document_text)

            expected = rec.decision
            curr_match = (curr_res.decision == expected or (expected == "REJECT" and curr_res.decision == "AUTO_REJECT") or (expected == "ACCEPT" and curr_res.decision == "AUTO_ACCEPT"))
            cand_match = (cand_res.decision == expected or (expected == "REJECT" and cand_res.decision == "AUTO_REJECT") or (expected == "ACCEPT" and cand_res.decision == "AUTO_ACCEPT"))

            if curr_match:
                correct_current += 1
            if cand_match:
                correct_candidate += 1
            elif curr_match and not cand_match:
                regressions.append(f"Regression on document '{rec.document_id}' for labels {rec.labels}")

        curr_acc = round(correct_current / len(self.golden_set), 2)
        cand_acc = round(correct_candidate / len(self.golden_set), 2)

        if regressions:
            return PromotionGateResult(
                promoted=False,
                current_accuracy=curr_acc,
                candidate_accuracy=cand_acc,
                reason=f"Candidate policy failed promotion gate due to {len(regressions)} regressions.",
                label_regressions=regressions
            )

        if cand_acc >= min_accuracy_threshold and cand_acc >= curr_acc:
            return PromotionGateResult(
                promoted=True,
                current_accuracy=curr_acc,
                candidate_accuracy=cand_acc,
                reason="Candidate policy passed Golden Set benchmark and promotion gate."
            )

        return PromotionGateResult(
            promoted=False,
            current_accuracy=curr_acc,
            candidate_accuracy=cand_acc,
            reason=f"Candidate accuracy ({cand_acc}) below minimum required threshold ({min_accuracy_threshold})."
        )
