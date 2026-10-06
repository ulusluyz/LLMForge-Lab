import os
import pytest
from llmforge.pipeline.v3 import CorpusPipelineV3, CorpusRecord

def test_pipeline_v3_resume_checkpoint(tmp_path):
    # Phase 1: Process initial record batch and save checkpoint
    pipeline1 = CorpusPipelineV3(str(tmp_path))
    records_batch1 = [
        CorpusRecord(id="1", text="Türkiye başkenti Ankara'dır.", status="ACCEPT")
    ]
    cleaned1 = pipeline1.process_records(records_batch1)
    assert len(cleaned1) == 1
    assert os.path.exists(tmp_path / "checkpoint.json")

    # Phase 2: Create new pipeline instance and load checkpoint
    pipeline2 = CorpusPipelineV3(str(tmp_path))
    loaded = pipeline2.load_checkpoint()
    assert loaded is True

    # Phase 3: Process second batch containing identical text
    records_batch2 = [
        CorpusRecord(id="2", text="Türkiye başkenti Ankara'dır.", status="ACCEPT") # duplicate from batch 1
    ]
    cleaned2 = pipeline2.process_records(records_batch2)
    assert len(cleaned2) == 0 # correctly recognized duplicate across resumed session
