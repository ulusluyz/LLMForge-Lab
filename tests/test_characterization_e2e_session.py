import pytest
from llmforge.intelligence.provider import MockProvider
from llmforge.models.adapters import SubprocessCLIAdapter
from llmforge.characterization.session import AdaptiveCharacterizationSession
from llmforge.characterization.boundary import CapabilityBoundaryDiscoverer
from llmforge.characterization.reproduction import FailureReproductionRunner
from llmforge.diagnostics.ladder import DiagnosticEscalationLadder, EscalationLevel

@pytest.mark.asyncio
async def test_full_characterization_e2e_workflow():
    provider = MockProvider({})
    adapter = SubprocessCLIAdapter({"command": "python3 -u -m tests.fixtures.dummy_model"})

    # 1. Start Adaptive Characterization Session
    session = AdaptiveCharacterizationSession(adapter, provider, model_name="Llama-3-7B-Turkish", parameter_count_b=7.0)
    session_result = await session.run_session(max_turns=12)

    assert session_result["turns_executed"] == 12
    profile = session_result["profile"]
    assert len(profile.strongest_capabilities) >= 1

    # 2. Discover Capability Boundaries
    boundary = CapabilityBoundaryDiscoverer.discover_reasoning_boundary(max_steps=8)
    assert boundary.max_passing_threshold == 4
    assert boundary.failing_threshold == 6

    # 3. Verify Failure Reproduction
    reproduction = FailureReproductionRunner.run_reproduction_tests(
        "LENGTH_CONSTRAINT_VIOLATION",
        "18-22 satır arasında anlat.",
        "Satır 1..."
    )
    assert reproduction.reproduced is True

    # 4. Escalate Fault Localization via Evidence
    diff_evidence = {"adapter_failed": True, "direct_runtime_passed": True}
    escalation = DiagnosticEscalationLadder.escalate_investigation("Adapter history failure", differential_evidence=diff_evidence)
    assert escalation.escalation_level == EscalationLevel.LEVEL_2_DIFFERENTIAL
    assert escalation.artifact == "src/llmforge/models/adapters.py"
    assert escalation.confidence == 0.95
