import pytest
from llmforge.models.adapters import SubprocessCLIAdapter, GenericHTTPAdapter
from llmforge.intelligence.provider import MockProvider
from pydantic import BaseModel

class DummySchema(BaseModel):
    message: str
    status: int

@pytest.mark.asyncio
async def test_subprocess_adapter():
    config = {
        "command": "python3 -m tests.fixtures.dummy_model",
        "model_name": "TestDummyModel"
    }
    adapter = SubprocessCLIAdapter(config)
    started = await adapter.start()
    assert started is True

    res = await adapter.generate("Türkiye'nin başkenti neresi?")
    assert res.status == "SUCCESS"
    assert "Ankara" in res.text

    model_info = await adapter.inspect_model()
    assert model_info.model_name == "TestDummyModel"
    assert model_info.context_length == "UNKNOWN"

    await adapter.stop()

@pytest.mark.asyncio
async def test_mock_intelligence_provider():
    provider = MockProvider({
        "responses": {
            "DummySchema": {"message": "hello", "status": 200},
            "default_text": "sample text"
        }
    })

    text = await provider.generate_text("Hi")
    assert text == "sample text"

    struct = await provider.generate_structured("Hi", DummySchema)
    assert struct.message == "hello"
    assert struct.status == 200
