import pytest
from llmforge.intelligence.provider import MockProvider
from llmforge.models.adapters import SubprocessCLIAdapter
from llmforge.diagnostics.engine import AdaptiveDiagnosticEngine

@pytest.mark.asyncio
async def test_diagnostic_engine_run():
    intelligence = MockProvider({})
    model = SubprocessCLIAdapter({"command": "python3 -u -m tests.fixtures.dummy_model"})

    engine = AdaptiveDiagnosticEngine(intelligence, model)
    report = await engine.run_diagnostic_run("test_run_001", max_turns=8)

    assert report.run_id == "test_run_001"
    assert report.total_turns == 8
    assert "clarity" in report.metrics_summary
    assert len(engine.graph.nodes) == 8
    assert len(engine.graph.edges) >= 1
