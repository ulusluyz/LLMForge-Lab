import os
import pytest
from llmforge.diagnostics.intervention_store import InterventionMemoryStore, InterventionRecord

def test_intervention_memory_store(tmp_path):
    store = InterventionMemoryStore(str(tmp_path))

    rec = InterventionRecord(
        intervention_id="int_01",
        run_id="run_01",
        problem_summary="History forwarding truncation in SubprocessCLIAdapter",
        primary_root_cause="LLMFORGE_INTEGRATION",
        recommended_intervention="LLMFORGE_INTEGRATION_FIX",
        human_decision="ACCEPT",
        applied_status="SUCCESS",
        human_notes="Fixed stdin flush buffer."
    )

    store.save_record(rec)
    loaded = store.load_all_records()
    assert len(loaded) == 1
    assert loaded[0].intervention_id == "int_01"
    assert loaded[0].applied_status == "SUCCESS"

    successful = store.get_successful_interventions_for_cause("LLMFORGE_INTEGRATION")
    assert len(successful) == 1
    assert successful[0].recommended_intervention == "LLMFORGE_INTEGRATION_FIX"
