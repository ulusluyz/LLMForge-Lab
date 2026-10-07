import pytest
from llmforge.diagnostics.root_cause import CompetingHypothesesEngine, RootCauseFamily, HypothesisStatus

def test_competing_hypotheses_engine():
    engine = CompetingHypothesesEngine()

    # Propose competing hypotheses for long-context instruction loss
    hyp_adapter = engine.propose_hypothesis(
        "hyp_01",
        RootCauseFamily.LLMFORGE_INTEGRATION,
        "ADAPTER_HISTORY_TRUNCATION",
        ["History forwarding payload truncated in adapter."],
        confidence=0.70
    )

    hyp_data = engine.propose_hypothesis(
        "hyp_02",
        RootCauseFamily.DATA_CORPUS,
        "LONG_CONTEXT_DATA_DEFICIENCY",
        ["Model failed multi-turn recall test."],
        confidence=0.40
    )

    ranked_before = engine.get_ranked_hypotheses()
    assert len(ranked_before) == 2
    assert ranked_before[0].hypothesis_id == "hyp_01"

    # Falsify data deficiency hypothesis via adapter vs direct runtime experiment
    engine.apply_experiment_evidence(
        "hyp_02",
        falsified=True,
        evidence_note="Direct runtime execution passed recall test; data deficiency falsified.",
        new_confidence=0.0
    )

    # Confirm adapter history truncation hypothesis
    engine.apply_experiment_evidence(
        "hyp_01",
        falsified=False,
        evidence_note="Subprocess adapter stdin buffer truncation reproduced.",
        new_confidence=0.92
    )

    ranked_after = engine.get_ranked_hypotheses()
    assert len(ranked_after) == 1
    assert ranked_after[0].hypothesis_id == "hyp_01"
    assert ranked_after[0].status == HypothesisStatus.CONFIRMED
    assert engine.hypotheses["hyp_02"].status == HypothesisStatus.FALSIFIED
