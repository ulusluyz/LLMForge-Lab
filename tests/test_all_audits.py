import os
import pytest
from llmforge.audit.engine import AuditEngine

def test_all_11_audits(tmp_path):
    audit_engine = AuditEngine(str(tmp_path))

    audits = [
        audit_engine.run_preflight_audit({"local_model_accessible": True, "api_key_present": True}),
        audit_engine.run_runtime_audit({"context_length": 4096}),
        audit_engine.run_diagnostic_audit({"turns": 20}),
        audit_engine.run_source_audit({"source_url": "https://example.com"}),
        audit_engine.run_pipeline_audit({"dedup_count": 10}),
        audit_engine.run_corpus_quality_audit({"language": "tr"}),
        audit_engine.run_human_review_audit({"approved": 5}),
        audit_engine.run_reproducibility_audit({"git_commit": "abc1234"}),
        audit_engine.run_security_audit({"prompt_injection_safe": True}),
        audit_engine.run_regression_audit({"score_delta": +0.05}),
        audit_engine.run_final_audit({"diagnostics_complete": True})
    ]

    assert len(audits) == 11
    for a in audits:
        assert a.status in ["PASS", "PASS_WITH_WARNINGS"]
        assert len(a.hash_signature) == 64

    audit_files = os.listdir(tmp_path / "audits")
    assert len(audit_files) == 11
