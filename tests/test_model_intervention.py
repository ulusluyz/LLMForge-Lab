import pytest
from llmforge.diagnostics.root_cause import CompetingHypothesesEngine, RootCauseFamily
from llmforge.diagnostics.intervention import ModelInterventionEngine, DataRecommendationGate

def test_model_intervention_engine_and_data_gate():
    engine = CompetingHypothesesEngine()

    # Scenario A: Technical system failure exists alongside weak data gap hypothesis -> DATA_REQUIREMENT MUST BE BLOCKED
    engine.propose_hypothesis("h1", RootCauseFamily.LLMFORGE_INTEGRATION, "ADAPTER_HISTORY_TRUNCATION", ["Adapter stdin buffer truncated"], 0.80)
    engine.propose_hypothesis("h2", RootCauseFamily.DATA_CORPUS, "DATA_DEFICIENCY", ["Multi-turn recall failure"], 0.40)

    hypotheses = engine.get_ranked_hypotheses()
    permitted, reason = DataRecommendationGate.is_data_recommendation_permitted(hypotheses)
    assert permitted is False
    assert "Data requirement blocked" in reason

    intervention_engine = ModelInterventionEngine()
    recs = intervention_engine.generate_recommendations(hypotheses)
    assert len(recs) == 1
    assert recs[0].recommended_intervention == "LLMFORGE_INTEGRATION_FIX"
    assert recs[0].data_required == "NO"

    # Scenario B: Technical alternatives falsified and genuine data gap confirmed -> DATA_REQUIREMENT PERMITTED
    engine.apply_experiment_evidence("h1", falsified=True, evidence_note="Adapter buffer test clean", new_confidence=0.0)
    engine.apply_experiment_evidence("h2", falsified=False, evidence_note="Genuine domain knowledge gap confirmed across direct runtime", new_confidence=0.90)

    hypotheses_b = engine.get_ranked_hypotheses()
    permitted_b, reason_b = DataRecommendationGate.is_data_recommendation_permitted(hypotheses_b)
    assert permitted_b is True
    assert "Data requirement permitted" in reason_b

    recs_b = intervention_engine.generate_recommendations(hypotheses_b)
    assert len(recs_b) == 1
    assert recs_b[0].recommended_intervention == "DATA_REQUIREMENT"
    assert recs_b[0].data_required == "YES"
