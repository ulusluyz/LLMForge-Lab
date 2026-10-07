import pytest
from llmforge.characterization.context_decomposition import StatefulScenarioTracker, ContextDecompositionScores

def test_context_decomposition():
    scores = StatefulScenarioTracker.evaluate_scenario_turn(
        turn_index=8,
        prompt="İlk bölümde bahsedilen Selin'in çantasındaki nesne neydi?",
        response_text="Selin'in çantasında kütüphane kartı vardı.",
        context_state={"entities": ["Selin"], "attributes": {"Selin": "kütüphane kartı"}}
    )

    assert scores.direct_recall >= 0.90
    assert scores.delayed_recall >= 0.90
    assert scores.multi_hop_composition == 0.35 # Correctly isolates multi-hop weakness
