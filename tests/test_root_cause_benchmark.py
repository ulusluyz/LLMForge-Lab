import pytest
from llmforge.diagnostics.root_cause import CompetingHypothesesEngine, RootCauseFamily, HypothesisStatus
from llmforge.diagnostics.planner import DiagnosticExperimentPlanner
from llmforge.diagnostics.intervention import ModelInterventionEngine, DataRecommendationGate

def test_root_cause_and_anti_data_bias_benchmark():
    # 1. Benchmark Scenario A: Adapter History Forwarding Failure (Technical System Bug)
    engine_a = CompetingHypothesesEngine()
    engine_a.propose_hypothesis("h_adapter", RootCauseFamily.LLMFORGE_INTEGRATION, "ADAPTER_HISTORY_TRUNCATION", ["CLI adapter stdin buffer truncated"], 0.85)
    engine_a.propose_hypothesis("h_data", RootCauseFamily.DATA_CORPUS, "TURKISH_DATA_DEFICIENCY", ["Multi-turn recall failure"], 0.45)

    hyps_a = engine_a.get_ranked_hypotheses()
    assert hyps_a[0].hypothesis_id == "h_adapter"

    # Verify Anti-Data-Bias Gate BLOCKS data requirement
    permitted_a, reason_a = DataRecommendationGate.is_data_recommendation_permitted(hyps_a)
    assert permitted_a is False
    assert "Data requirement blocked" in reason_a

    intervention_engine = ModelInterventionEngine()
    recs_a = intervention_engine.generate_recommendations(hyps_a)
    assert len(recs_a) == 1
    assert recs_a[0].recommended_intervention == "LLMFORGE_INTEGRATION_FIX"
    assert recs_a[0].data_required == "NO"

    # 2. Benchmark Scenario B: Tokenizer Subword Fertility Failure (Tokenizer Issue)
    engine_b = CompetingHypothesesEngine()
    engine_b.propose_hypothesis("h_tok", RootCauseFamily.TOKENIZER, "HIGH_SUBWORD_FERTILITY", ["High fertility on Turkish text"], 0.88)
    engine_b.propose_hypothesis("h_data_b", RootCauseFamily.DATA_CORPUS, "TURKISH_CORPUS_GAP", ["Grammar errors"], 0.35)

    hyps_b = engine_b.get_ranked_hypotheses()
    permitted_b, reason_b = DataRecommendationGate.is_data_recommendation_permitted(hyps_b)
    assert permitted_b is False

    recs_b = intervention_engine.generate_recommendations(hyps_b)
    assert len(recs_b) == 1
    assert recs_b[0].recommended_intervention == "TOKENIZER_CHANGE"
    assert recs_b[0].data_required == "NO"

    # 3. Benchmark Scenario C: Genuine Data Gap (Technical System Healthy)
    engine_c = CompetingHypothesesEngine()
    engine_c.propose_hypothesis("h_tok_c", RootCauseFamily.TOKENIZER, "HIGH_SUBWORD_FERTILITY", ["Tokenizer test clean"], 0.0)
    engine_c.apply_experiment_evidence("h_tok_c", falsified=True, evidence_note="Tokenizer fertility normal", new_confidence=0.0)

    engine_c.propose_hypothesis("h_data_c", RootCauseFamily.DATA_CORPUS, "GENUINE_TURKISH_DOMAIN_GAP", ["Domain knowledge gap across direct runtime"], 0.90)

    hyps_c = engine_c.get_ranked_hypotheses()
    permitted_c, reason_c = DataRecommendationGate.is_data_recommendation_permitted(hyps_c)
    assert permitted_c is True
    assert "Data requirement permitted" in reason_c

    recs_c = intervention_engine.generate_recommendations(hyps_c)
    assert len(recs_c) == 1
    assert recs_c[0].recommended_intervention == "DATA_REQUIREMENT"
    assert recs_c[0].data_required == "YES"
