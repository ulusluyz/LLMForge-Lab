import pytest
from llmforge.characterization.profile import CapabilityProfileEngine, CapabilityFamily, CapabilityClassification
from llmforge.characterization.envelope import ExpectedCapabilityEnvelope

def test_profile_engine_and_envelope():
    envelope = ExpectedCapabilityEnvelope(parameter_count_b=7.0)
    exp_formal = envelope.get_expected_score("formal_turkish")
    assert exp_formal == 0.85

    engine = CapabilityProfileEngine(model_name="Llama-3-7B-Turkish", parameter_count_b=7.0)

    # Record strong formal Turkish evidence
    engine.record_capability_evidence("formal_turkish", CapabilityFamily.LANGUAGE_LINGUISTIC, 0.95, exp_formal)
    # Record unexpectedly weak reasoning evidence
    engine.record_capability_evidence("casual_chat", CapabilityFamily.GENERATION, 0.40, expected_score=0.75)

    profile = engine.finalize_profile()
    assert len(profile.strongest_capabilities) == 1
    assert profile.strongest_capabilities[0].capability_name == "formal_turkish"
    assert profile.strongest_capabilities[0].is_preservation_target is True

    assert len(profile.unexpected_weaknesses) == 1
    assert profile.unexpected_weaknesses[0].capability_name == "casual_chat"
    assert profile.unexpected_weaknesses[0].classification == CapabilityClassification.UNEXPECTED_WEAKNESS
