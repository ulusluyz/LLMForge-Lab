import pytest
from llmforge.intelligence.provider import MockProvider
from llmforge.models.adapters import SubprocessCLIAdapter
from llmforge.characterization.session import AdaptiveCharacterizationSession

@pytest.mark.asyncio
async def test_adaptive_characterization_session():
    provider = MockProvider({})
    adapter = SubprocessCLIAdapter({"command": "python3 -u -m tests.fixtures.dummy_model"})

    session = AdaptiveCharacterizationSession(adapter, provider, model_name="TestModel", parameter_count_b=7.0)
    result = await session.run_session(max_turns=12)

    assert result["turns_executed"] == 12
    assert "profile" in result
    assert len(result["profile"].strongest_capabilities) >= 1
    assert len(result["recommendations"]) >= 1
    assert result["recommendations"][0].recommended_intervention == "LLMFORGE_INTEGRATION_FIX"
