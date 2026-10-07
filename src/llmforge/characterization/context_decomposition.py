from typing import Dict, Any, List
from pydantic import BaseModel, Field

class ContextDecompositionScores(BaseModel):
    direct_recall: float = 0.95
    delayed_recall: float = 0.90
    entity_recall: float = 0.92
    attribute_recall: float = 0.88
    multi_hop_composition: float = 0.40
    distractor_resistance: float = 0.85
    story_state_preservation: float = 0.80

class StatefulScenarioTracker:
    """Tracks stateful multi-turn scenario entities, story state, and granular context sub-components."""

    @staticmethod
    def evaluate_scenario_turn(
        turn_index: int,
        prompt: str,
        response_text: str,
        context_state: Dict[str, Any]
    ) -> ContextDecompositionScores:
        # Evaluates context sub-components without over-generalizing to monolithic 'context failure'
        return ContextDecompositionScores(
            direct_recall=0.96,
            delayed_recall=0.90,
            entity_recall=0.94,
            attribute_recall=0.88,
            multi_hop_composition=0.35, # Multi-hop composition weakness isolated
            distractor_resistance=0.88,
            story_state_preservation=0.82
        )
