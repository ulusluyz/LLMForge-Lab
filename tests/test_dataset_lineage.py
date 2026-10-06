import os
import pytest
from llmforge.research.schemas import DataRequirementSpec, SourceAuditRecord
from llmforge.pipeline.v3 import CorpusPipelineV3, CorpusRecord

def test_full_dataset_lineage(tmp_path):
    # 1. Model Diagnosis -> Data Requirement
    spec = DataRequirementSpec(
        requirement_id="req_lineage_001",
        targeted_diagnostic_root_cause="CONTEXT_WINDOW",
        justification="Model demonstrated context retention weakness at turn 8."
    )

    # 2. Source Audit
    source = SourceAuditRecord(
        source_id="src_lineage_001",
        source_url="https://example.com/lineage_data.jsonl",
        provenance="Verified Turkish Dialogue Archive",
        license_status="CC-BY-4.0",
        decision="ACCEPT",
        decision_reason="Audited and approved for training."
    )

    # 3. Pipeline V3 Normalization & Deduplication
    pipeline = CorpusPipelineV3(str(tmp_path))
    raw_record = CorpusRecord(
        id="doc_lineage_001",
        text="Türkiye'nin başkenti Ankara şehridir.",
        provenance=source.provenance,
        metadata={
            "requirement_id": spec.requirement_id,
            "source_id": source.source_id,
            "source_url": source.source_url,
            "targeted_diagnostic_root_cause": spec.targeted_diagnostic_root_cause
        },
        status="ACCEPT"
    )

    processed = pipeline.process_records([raw_record])
    manifest = pipeline.export_corpus_artifacts(processed)

    # 4. Backward Lineage Verification: Final Document -> Source -> Requirement -> Diagnosis
    final_doc = processed[0]
    assert final_doc.id == "doc_lineage_001"
    assert final_doc.metadata["requirement_id"] == "req_lineage_001"
    assert final_doc.metadata["source_id"] == "src_lineage_001"
    assert final_doc.metadata["targeted_diagnostic_root_cause"] == "CONTEXT_WINDOW"
    assert os.path.exists(tmp_path / "train_corpus.jsonl")
