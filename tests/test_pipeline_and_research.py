import os
import pytest
from llmforge.research.schemas import DataRequirementSpec
from llmforge.research.adapters import MockResearchAdapter
from llmforge.pipeline.v3 import CorpusPipelineV3, CorpusRecord

@pytest.mark.asyncio
async def test_source_research_mock():
    adapter = MockResearchAdapter()
    spec = DataRequirementSpec(
        requirement_id="req_001",
        targeted_diagnostic_root_cause="CONTEXT_WINDOW",
        justification="Needs more Turkish multi-turn dialogue data"
    )
    sources = await adapter.discover_sources(spec)
    assert len(sources) == 2
    assert sources[0].decision == "ACCEPT"
    assert sources[1].decision == "HUMAN_REVIEW"

def test_pipeline_v3_dedup_and_checkpoint(tmp_path):
    pipeline = CorpusPipelineV3(str(tmp_path))
    records = [
        CorpusRecord(id="1", text="Türkiye başkenti Ankara'dır.", status="ACCEPT"),
        CorpusRecord(id="2", text="Türkiye başkenti Ankara'dır.", status="ACCEPT"), # duplicate
        CorpusRecord(id="3", text="Kısa", status="ACCEPT") # too short
    ]

    cleaned = pipeline.process_records(records)
    assert len(cleaned) == 1
    assert cleaned[0].id == "1"

    manifest = pipeline.export_corpus_artifacts(records)
    assert manifest["accepted_count"] == 1
    assert os.path.exists(tmp_path / "train_corpus.jsonl")
    assert os.path.exists(tmp_path / "manifest.json")
