import os
import pytest
from llmforge.audit.engine import AuditEngine

def test_audit_engine(tmp_path):
    audit_engine = AuditEngine(str(tmp_path))

    preflight = audit_engine.run_preflight_audit({
        "local_model_accessible": True,
        "api_key_present": False
    })
    assert preflight.status == "PASS_WITH_WARNINGS"
    assert len(preflight.hash_signature) == 64
    assert os.path.exists(tmp_path / "audits" / "preflight_audit.json")

    final_audit = audit_engine.run_final_audit({"diagnostics_complete": True})
    assert final_audit.status == "PASS"
    assert os.path.exists(tmp_path / "audits" / "final_audit.json")
