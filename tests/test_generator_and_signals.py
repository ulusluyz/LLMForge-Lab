import pytest
from llmforge.characterization.generator import DynamicItemGenerator
from llmforge.characterization.signals import MultiSignalExtractor

def test_dynamic_generator_and_multi_signal_extractor():
    # 1. Generate dynamic prompt
    item1 = DynamicItemGenerator.generate_dynamic_prompt("narrative_multi_constraint", turn_index=1, seed=10)
    item2 = DynamicItemGenerator.generate_dynamic_prompt("narrative_multi_constraint", turn_index=1, seed=20)

    # Dynamic prompts vary prompt surface wording while keeping constraints stable
    assert item1["prompt"] != item2["prompt"]
    assert item1["constraints"]["min_lines"] == 18

    # 2. Extract multi-signal evidence from response containing required entities
    names = item1["constraints"]["required_entities"]
    dummy_response = "\n".join([f"Satır {i}: Hikaye cümlesi {names[0]} {names[1]} {names[2]}." for i in range(1, 20)])

    res = MultiSignalExtractor.extract_signals(dummy_response, item1["constraints"])
    assert res.deterministic_checks_passed is True
    assert res.signals["length_constraint"].value == 1.0
    assert res.signals["entity_tracking"].value == 1.0
    assert "turkish_fluency" in res.signals
