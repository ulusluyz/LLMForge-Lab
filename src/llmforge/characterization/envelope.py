from pydantic import BaseModel
from llmforge.characterization.profile import CapabilityFamily

class ExpectedCapabilityEnvelope(BaseModel):
    """Estimates baseline expectation scores for capability families based on parameter count and architectural metadata."""

    parameter_count_b: float = 7.0
    context_length_tokens: int = 4096
    is_instruction_tuned: bool = True

    def get_expected_score(self, capability_name: str) -> float:
        # Base expectation derived from parameter scale
        if self.parameter_count_b < 3.0:
            base = 0.60
        elif self.parameter_count_b <= 13.0:
            base = 0.75
        else:
            base = 0.85

        # Domain/task-specific expectation heuristics
        cap_lower = capability_name.lower()
        if "reasoning" in cap_lower or "multi_step" in cap_lower:
            return max(0.40, base - 0.20)
        if "formal" in cap_lower or "grammar" in cap_lower:
            return min(0.95, base + 0.10)

        return base
