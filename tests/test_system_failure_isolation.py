import pytest
from llmforge.intelligence.provider import MockProvider
from llmforge.models.adapters import SubprocessCLIAdapter
from llmforge.diagnostics.engine import AdaptiveDiagnosticEngine

@pytest.mark.asyncio
async def test_system_vs_model_failure_isolation():
    intelligence = MockProvider({})
    model = SubprocessCLIAdapter({"command": "python3 -u -m tests.fixtures.dummy_model"})

    engine = AdaptiveDiagnosticEngine(intelligence, model)
    # Artificially disable history forwarding to simulate a system error
    engine.history_forwarding_enabled = False

    report = await engine.run_diagnostic_run("test_sys_failure_001", max_turns=8)

    assert report.run_id == "test_sys_failure_001"
    assert engine.system_failure_detected is True
    assert len(report.root_causes) == 1
    assert report.root_causes[0].category == "LLMFORGE_SYSTEM_ERROR"
    assert "Do not train or blame model" in report.root_causes[0].reason_for_action
