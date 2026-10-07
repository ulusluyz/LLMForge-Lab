from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class CapabilityClassification(str, Enum):
    STRENGTH = "STRENGTH"
    NORMAL = "NORMAL"
    WEAKNESS = "WEAKNESS"
    ANOMALY = "ANOMALY"
    UNEXPECTED_STRENGTH = "UNEXPECTED_STRENGTH"
    UNEXPECTED_WEAKNESS = "UNEXPECTED_WEAKNESS"
    PRESERVATION_TARGET = "PRESERVATION_TARGET"

class CapabilityFamily(str, Enum):
    LANGUAGE_LINGUISTIC = "LANGUAGE_LINGUISTIC"
    TEXT_UNDERSTANDING = "TEXT_UNDERSTANDING"
    TRANSFORMATION = "TRANSFORMATION"
    GENERATION = "GENERATION"
    REASONING = "REASONING"
    KNOWLEDGE = "KNOWLEDGE"
    CONTEXT_MEMORY = "CONTEXT_MEMORY"
    ROBUSTNESS_CALIBRATION = "ROBUSTNESS_CALIBRATION"

class CapabilityScore(BaseModel):
    capability_name: str
    family: CapabilityFamily
    observed_score: float # 0.0 to 1.0
    expected_score: float = 0.70 # Baseline expectation from envelope
    classification: CapabilityClassification = CapabilityClassification.NORMAL
    evidence_count: int = 0
    is_preservation_target: bool = False

class CapabilityProfile(BaseModel):
    model_name: str
    parameter_count_b: float = 7.0
    context_length_tokens: int = 4096
    strongest_capabilities: List[CapabilityScore] = Field(default_factory=list)
    weakest_capabilities: List[CapabilityScore] = Field(default_factory=list)
    unexpected_strengths: List[CapabilityScore] = Field(default_factory=list)
    unexpected_weaknesses: List[CapabilityScore] = Field(default_factory=list)
    preservation_targets: List[CapabilityScore] = Field(default_factory=list)
    all_scores: Dict[str, CapabilityScore] = Field(default_factory=dict)

class CapabilityProfileEngine:
    """Engine compiling multi-signal evidence into holistic Model Capability Profiles."""

    def __init__(self, model_name: str = "TargetModel", parameter_count_b: float = 7.0):
        self.profile = CapabilityProfile(model_name=model_name, parameter_count_b=parameter_count_b)

    def record_capability_evidence(
        self,
        capability_name: str,
        family: CapabilityFamily,
        score: float,
        expected_score: float = 0.70
    ) -> None:
        curr = self.profile.all_scores.get(capability_name)
        if curr:
            new_count = curr.evidence_count + 1
            new_score = round((curr.observed_score * curr.evidence_count + score) / new_count, 2)
            curr.observed_score = new_score
            curr.evidence_count = new_count
        else:
            curr = CapabilityScore(
                capability_name=capability_name,
                family=family,
                observed_score=score,
                expected_score=expected_score,
                evidence_count=1
            )
            self.profile.all_scores[capability_name] = curr

        # Determine classification vs expected envelope
        diff = curr.observed_score - curr.expected_score
        if curr.observed_score >= 0.85:
            if diff >= 0.20:
                curr.classification = CapabilityClassification.UNEXPECTED_STRENGTH
            else:
                curr.classification = CapabilityClassification.STRENGTH
            curr.is_preservation_target = True
        elif curr.observed_score <= 0.50:
            if diff <= -0.20:
                curr.classification = CapabilityClassification.UNEXPECTED_WEAKNESS
            else:
                curr.classification = CapabilityClassification.WEAKNESS
        else:
            curr.classification = CapabilityClassification.NORMAL

    def finalize_profile(self) -> CapabilityProfile:
        scores = list(self.profile.all_scores.values())
        self.profile.strongest_capabilities = sorted([s for s in scores if s.classification in [CapabilityClassification.STRENGTH, CapabilityClassification.UNEXPECTED_STRENGTH]], key=lambda x: x.observed_score, reverse=True)
        self.profile.weakest_capabilities = sorted([s for s in scores if s.classification in [CapabilityClassification.WEAKNESS, CapabilityClassification.UNEXPECTED_WEAKNESS]], key=lambda x: x.observed_score)
        self.profile.unexpected_strengths = [s for s in scores if s.classification == CapabilityClassification.UNEXPECTED_STRENGTH]
        self.profile.unexpected_weaknesses = [s for s in scores if s.classification == CapabilityClassification.UNEXPECTED_WEAKNESS]
        self.profile.preservation_targets = [s for s in scores if s.is_preservation_target]
        return self.profile
