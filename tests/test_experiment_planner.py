import pytest
from llmforge.diagnostics.root_cause import CompetingHypothesesEngine, RootCauseFamily
from llmforge.diagnostics.planner import DiagnosticExperimentPlanner

def test_diagnostic_experiment_planner():
    engine = CompetingHypothesesEngine()
    engine.propose_hypothesis("h1", RootCauseFamily.LLMFORGE_INTEGRATION, "ADAPTER_BUG", ["Adapter failure"], 0.70)
    engine.propose_hypothesis("h2", RootCauseFamily.DATA_CORPUS, "DATA_GAP", ["Model recall failure"], 0.40)

    hypotheses = engine.get_ranked_hypotheses()
    exp = DiagnosticExperimentPlanner.plan_next_best_experiment(hypotheses)

    assert exp is not None
    assert exp.comparison_type == "ADAPTER_VS_DIRECT_RUNTIME"
    assert exp.diagnostic_value_score >= 0.95
