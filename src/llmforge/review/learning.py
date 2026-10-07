import os
import json
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
from llmforge.review.store import HumanFeedbackStore, HumanReviewRecord
from llmforge.review.registry import LabelRegistry

class LearnedPattern(BaseModel):
    label_id: str
    pattern_text: str
    is_counter_example: bool = False
    weight: float = 1.0
    source_record_id: str

class DecisionResult(BaseModel):
    decision: str # AUTO_ACCEPT, AUTO_REJECT, HUMAN_REVIEW
    confidence: float
    assigned_labels: List[str] = Field(default_factory=list)
    escalation_reason: str = ""
    matching_patterns: List[str] = Field(default_factory=list)
    counter_patterns: List[str] = Field(default_factory=list)
    novelty_score: float = 0.0

class ThreeLayerLearningEngine:
    """Three-Layer Learning Engine: Layer A (Raw Evidence), Layer B (Learned Patterns/Counter-Examples), Layer C (Decision & Active Learning)."""

    def __init__(self, store: HumanFeedbackStore, registry: LabelRegistry):
        self.store = store
        self.registry = registry
        self.learned_patterns: List[LearnedPattern] = []
        self.rebuild_learned_knowledge()

    def rebuild_learned_knowledge(self) -> None:
        """Rebuild Layer B knowledge from raw verified human feedback records."""
        self.learned_patterns.clear()
        records = self.store.load_all_records()

        for rec in records:
            # Extract passage-level positive patterns
            for passage in rec.passage_annotations:
                for lbl in passage.labels:
                    self.learned_patterns.append(LearnedPattern(
                        label_id=lbl,
                        pattern_text=passage.selected_text.lower().strip(),
                        is_counter_example=False,
                        weight=1.5 if rec.is_correction else 1.0,
                        source_record_id=rec.review_id
                    ))

            # Extract document-level patterns if no passage annotations specified
            if not rec.passage_annotations and rec.decision in ["REJECT", "HUMAN_REVIEW"]:
                for lbl in rec.labels:
                    self.learned_patterns.append(LearnedPattern(
                        label_id=lbl,
                        pattern_text=rec.document_text.lower().strip()[:100],
                        is_counter_example=False,
                        weight=1.0,
                        source_record_id=rec.review_id
                    ))

            # Extract counter-examples from registered taxonomy definitions
            for lbl in rec.labels:
                label_def = self.registry.get_label(lbl)
                if label_def:
                    for counter_ex in label_def.counter_examples:
                        self.learned_patterns.append(LearnedPattern(
                            label_id=lbl,
                            pattern_text=counter_ex.lower().strip(),
                            is_counter_example=True,
                            weight=1.5,
                            source_record_id=rec.review_id
                        ))

    def evaluate_document(self, text: str, threshold: float = 0.85) -> DecisionResult:
        """Layer C Decision Logic: Evaluate incoming document against learned knowledge."""
        text_lower = text.lower()
        matched_pos: Dict[str, float] = {}
        matched_counter: Dict[str, float] = {}

        for pattern in self.learned_patterns:
            if pattern.pattern_text in text_lower:
                if pattern.is_counter_example:
                    matched_counter[pattern.label_id] = matched_counter.get(pattern.label_id, 0.0) + pattern.weight
                else:
                    matched_pos[pattern.label_id] = matched_pos.get(pattern.label_id, 0.0) + pattern.weight

        # Check for active learning escalation when counter-example is detected alongside positive pattern
        if matched_pos and matched_counter:
            return DecisionResult(
                decision="HUMAN_REVIEW",
                confidence=0.50,
                assigned_labels=list(matched_pos.keys()),
                escalation_reason="Active Learning Escalation: Conflicting positive and counter-examples detected.",
                matching_patterns=list(matched_pos.keys()),
                counter_patterns=list(matched_counter.keys()),
                novelty_score=0.40
            )

        assigned_labels = list(matched_pos.keys())
        if assigned_labels:
            highest_risk = max([self.registry.get_label(l).risk_level if self.registry.get_label(l) else "LOW" for l in assigned_labels])
            if highest_risk in ["HIGH", "CRITICAL"]:
                return DecisionResult(
                    decision="HUMAN_REVIEW",
                    confidence=0.88,
                    assigned_labels=assigned_labels,
                    escalation_reason=f"High-Risk Label '{assigned_labels[0]}' assigned; human verification required.",
                    matching_patterns=list(matched_pos.keys()),
                    novelty_score=0.10
                )
            return DecisionResult(
                decision="AUTO_REJECT",
                confidence=0.92,
                assigned_labels=assigned_labels,
                escalation_reason="",
                matching_patterns=list(matched_pos.keys()),
                novelty_score=0.05
            )

        # Novelty / Out-of-Distribution Escalation
        if len(text_lower.split()) > 20 and not matched_pos:
            return DecisionResult(
                decision="HUMAN_REVIEW",
                confidence=0.60,
                assigned_labels=[],
                escalation_reason="Novelty Escalation: Out-of-distribution document structure.",
                novelty_score=0.85
            )

        return DecisionResult(
            decision="AUTO_ACCEPT",
            confidence=0.90,
            assigned_labels=[],
            escalation_reason="",
            novelty_score=0.0
        )
