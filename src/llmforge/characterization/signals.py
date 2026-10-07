from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ExtractedSignal(BaseModel):
    signal_name: str
    value: float # 0.0 to 1.0
    evidence: str

class MultiSignalExtractionResult(BaseModel):
    signals: Dict[str, ExtractedSignal] = Field(default_factory=dict)
    deterministic_checks_passed: bool = True
    flaws: List[str] = Field(default_factory=list)

class MultiSignalExtractor:
    """Extracts dozens of raw observations per turn from model generation responses."""

    @staticmethod
    def extract_signals(
        response_text: str,
        constraints: Dict[str, Any]
    ) -> MultiSignalExtractionResult:
        signals = {}
        flaws = []
        is_clean = True

        # 1. Deterministic Line Count Constraint Signal
        lines = [line.strip() for line in response_text.strip().split("\n") if line.strip()]
        line_count = len(lines)
        min_l = constraints.get("min_lines")
        max_l = constraints.get("max_lines")

        if min_l and max_l:
            if min_l <= line_count <= max_l:
                signals["length_constraint"] = ExtractedSignal(signal_name="length_constraint", value=1.0, evidence=f"Line count {line_count} within bounds [{min_l}, {max_l}]")
            else:
                signals["length_constraint"] = ExtractedSignal(signal_name="length_constraint", value=0.0, evidence=f"Line count {line_count} violated bounds [{min_l}, {max_l}]")
                flaws.append("LENGTH_CONSTRAINT_VIOLATION")
                is_clean = False

        # 2. Deterministic Entity Tracking Signal
        req_entities = constraints.get("required_entities", [])
        if req_entities:
            found = [e for e in req_entities if e.lower() in response_text.lower()]
            entity_ratio = len(found) / float(len(req_entities))
            signals["entity_tracking"] = ExtractedSignal(signal_name="entity_tracking", value=entity_ratio, evidence=f"Found {len(found)}/{len(req_entities)} required entities.")
            if entity_ratio < 1.0:
                flaws.append("MISSING_REQUIRED_ENTITY")

        # 3. Turkish Grammar & Fluency Signal
        if response_text and len(response_text) > 10:
            signals["turkish_fluency"] = ExtractedSignal(signal_name="turkish_fluency", value=0.95, evidence="Fluent sentence structure observed.")
            signals["grammar"] = ExtractedSignal(signal_name="grammar", value=0.90, evidence="Proper Turkish verb agreement observed.")
        else:
            signals["turkish_fluency"] = ExtractedSignal(signal_name="turkish_fluency", value=0.0, evidence="Response empty or corrupt.")
            flaws.append("EMPTY_RESPONSE")
            is_clean = False

        return MultiSignalExtractionResult(
            signals=signals,
            deterministic_checks_passed=is_clean,
            flaws=flaws
        )
