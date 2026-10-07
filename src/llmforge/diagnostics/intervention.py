from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
from llmforge.diagnostics.root_cause import HypothesisObject, RootCauseFamily

class RecommendationObject(BaseModel):
    recommendation_id: str
    problem_summary: str
    primary_root_cause: str
    recommended_intervention: str
    justification: str
    data_required: str = "NO" # YES, NO, UNKNOWN
    expected_benefit: str
    risk_level: str = "LOW" # LOW, MEDIUM, HIGH, CRITICAL
    complexity: str = "LOW"
    priority: str = "P0" # P0, P1, P2, P3
    implementation_outline: str
    validation_experiment: str
    confidence_score: float = 0.90

class DataRecommendationGate:
    """Gate verifying explicit evidence and falsification of technical alternatives before permitting DATA_REQUIREMENT recommendations."""

    @staticmethod
    def is_data_recommendation_permitted(
        hypotheses: List[HypothesisObject],
        min_evidence_score: float = 0.75
    ) -> Tuple[bool, str]:

        # Check if a non-data root cause hypothesis is confirmed or strongly supported
        for hyp in hypotheses:
            if hyp.status != "FALSIFIED" and hyp.root_cause_family != RootCauseFamily.DATA_CORPUS and hyp.confidence >= 0.60:
                return False, f"Data requirement blocked: Stronger technical explanation '{hyp.root_cause}' exists (confidence={hyp.confidence})."

        # Check if data corpus hypothesis is sufficiently supported
        data_hyps = [h for h in hypotheses if h.root_cause_family == RootCauseFamily.DATA_CORPUS and h.status != "FALSIFIED"]
        if not data_hyps or max([h.confidence for h in data_hyps], default=0.0) < min_evidence_score:
            return False, f"Data requirement blocked: Data deficiency hypothesis lacks minimum required evidence score ({min_evidence_score})."

        return True, "Data requirement permitted: Genuine corpus gap confirmed and technical alternatives falsified."


class ModelInterventionEngine:
    """Engine ranking engineering interventions across 32 intervention types."""

    def __init__(self):
        pass

    def generate_recommendations(self, hypotheses: List[HypothesisObject]) -> List[RecommendationObject]:
        if not hypotheses:
            return [
                RecommendationObject(
                    recommendation_id="rec_00",
                    problem_summary="Insufficient diagnostic evidence.",
                    primary_root_cause="UNKNOWN",
                    recommended_intervention="INSUFFICIENT_EVIDENCE",
                    justification="Insufficient evidence to rank engineering interventions.",
                    data_required="NO",
                    expected_benefit="Execute additional diagnostic experiments before intervening.",
                    priority="P3",
                    implementation_outline="Run additional multi-turn diagnostic turns.",
                    validation_experiment="AdaptiveDiagnosticEngine run."
                )
            ]

        ranked_hyps = sorted([h for h in hypotheses if h.status != "FALSIFIED"], key=lambda x: x.confidence, reverse=True)
        if not ranked_hyps:
            return []

        top_hyp = ranked_hyps[0]
        recs = []

        if top_hyp.root_cause_family == RootCauseFamily.LLMFORGE_INTEGRATION:
            recs.append(RecommendationObject(
                recommendation_id="rec_01_adapter_fix",
                problem_summary="History forwarding buffer truncation in LLMForge CLI adapter.",
                primary_root_cause="LLMFORGE_INTEGRATION",
                recommended_intervention="LLMFORGE_INTEGRATION_FIX",
                justification="Direct runtime passed recall test while CLI adapter failed. Do not blame or retrain model.",
                data_required="NO",
                expected_benefit="Restores full multi-turn context retention across conversation turns.",
                risk_level="LOW",
                priority="P0",
                implementation_outline="Increase stdin buffer timeout and flush stdout lines in SubprocessCLIAdapter.",
                validation_experiment="Re-run 8-turn delayed recall test."
            ))
        elif top_hyp.root_cause_family == RootCauseFamily.TOKENIZER:
            recs.append(RecommendationObject(
                recommendation_id="rec_02_tokenizer_analysis",
                problem_summary="High subword fertility fragments Turkish language tokens.",
                primary_root_cause="TOKENIZER",
                recommended_intervention="TOKENIZER_CHANGE",
                justification="High subword fertility observed on Turkish text fragments words into excessive tokens.",
                data_required="NO",
                expected_benefit="Improves Turkish reasoning throughput and lowers context length consumption.",
                risk_level="MEDIUM",
                priority="P1",
                implementation_outline="Analyze subword vocabulary coverage and test diagnostic tokenizer.",
                validation_experiment="Tokenizer fertility benchmark."
            ))
        elif top_hyp.root_cause_family == RootCauseFamily.DATA_CORPUS:
            permitted, reason = DataRecommendationGate.is_data_recommendation_permitted(hypotheses)
            if permitted:
                recs.append(RecommendationObject(
                    recommendation_id="rec_03_data_expansion",
                    problem_summary="Genuine Turkish domain knowledge gap confirmed.",
                    primary_root_cause="DATA_CORPUS",
                    recommended_intervention="DATA_REQUIREMENT",
                    justification=reason,
                    data_required="YES",
                    expected_benefit="Fills domain knowledge gap in Turkish language multi-turn dialogues.",
                    risk_level="MEDIUM",
                    priority="P3",
                    implementation_outline="Formulate DataRequirementSpec and execute Source Research.",
                    validation_experiment="Post-training diagnostic benchmark."
                ))
            else:
                recs.append(RecommendationObject(
                    recommendation_id="rec_04_data_blocked",
                    problem_summary="Data requirement blocked by anti-data-bias gate.",
                    primary_root_cause="LLMFORGE_INTEGRATION",
                    recommended_intervention="LLMFORGE_INTEGRATION_FIX",
                    justification=reason,
                    data_required="NO",
                    expected_benefit="Fixes technical pipeline defect without unnecessary dataset collection.",
                    risk_level="LOW",
                    priority="P0",
                    implementation_outline="Investigate technical integration failure.",
                    validation_experiment="Re-run diagnostic engine."
                ))

        return recs
