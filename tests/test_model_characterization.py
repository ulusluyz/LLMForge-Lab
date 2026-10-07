import pytest
from llmforge.characterization.profile import CapabilityProfileEngine, CapabilityFamily
from llmforge.characterization.envelope import ExpectedCapabilityEnvelope
from llmforge.characterization.generator import DynamicItemGenerator
from llmforge.characterization.signals import MultiSignalExtractor
from llmforge.characterization.boundary import CapabilityBoundaryDiscoverer
from llmforge.diagnostics.tokenizer_lab import TokenizerLab
from llmforge.diagnostics.ladder import DiagnosticEscalationLadder, EscalationLevel

def test_full_model_characterization_suite():
    # 1. Expected Capability Envelope
    envelope = ExpectedCapabilityEnvelope(parameter_count_b=7.0)
    exp_formal = envelope.get_expected_score("formal_turkish")
    assert exp_formal == 0.85

    # 2. Capability Profiling
    engine = CapabilityProfileEngine("Llama-3-7B", parameter_count_b=7.0)
    engine.record_capability_evidence("formal_turkish", CapabilityFamily.LANGUAGE_LINGUISTIC, 0.95, exp_formal)
    engine.record_capability_evidence("casual_chat", CapabilityFamily.GENERATION, 0.35, expected_score=0.75)
    profile = engine.finalize_profile()

    assert len(profile.strongest_capabilities) == 1
    assert profile.strongest_capabilities[0].is_preservation_target is True
    assert len(profile.unexpected_weaknesses) == 1

    # 3. Dynamic Prompt Surface Generation & Multi-Signal Extraction
    item = DynamicItemGenerator.generate_dynamic_prompt("narrative_multi_constraint", turn_index=1, seed=42)
    names = item["constraints"]["required_entities"]
    dummy_text = "\n".join([f"Satır {i}: Hikaye cümlesi {names[0]} {names[1]} {names[2]}." for i in range(1, 20)])

    extracted = MultiSignalExtractor.extract_signals(dummy_text, item["constraints"])
    assert extracted.deterministic_checks_passed is True
    assert extracted.signals["length_constraint"].value == 1.0

    # 4. Capability Boundary Discovery
    reasoning_bound = CapabilityBoundaryDiscoverer.discover_reasoning_boundary(max_steps=8)
    assert reasoning_bound.max_passing_threshold == 4
    assert reasoning_bound.failing_threshold == 6

    # 5. Tokenizer Lab
    tok_metrics = TokenizerLab.analyze_tokenizer("Türkiye'nin coğrafi bölgeleri")
    assert tok_metrics.is_turkish_optimized is True

    # 6. Diagnostic Escalation Ladder
    escalation = DiagnosticEscalationLadder.escalate_investigation("Adapter history forwarding failure")
    assert escalation.escalation_level == EscalationLevel.LEVEL_2_DIFFERENTIAL
