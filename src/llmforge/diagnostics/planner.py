from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from llmforge.diagnostics.root_cause import HypothesisObject, RootCauseFamily

class DiagnosticExperiment(BaseModel):
    experiment_id: str
    title: str
    target_hypotheses: List[str] = Field(default_factory=list)
    comparison_type: str # ADAPTER_VS_DIRECT_RUNTIME, RAW_VS_CHAT_MODE, SHORT_VS_LONG_CONTEXT, GREEDY_VS_SAMPLING
    description: str
    diagnostic_value_score: float = 0.90
    required_resources: List[str] = Field(default_factory=list)
    is_executable: bool = True

class DiagnosticExperimentPlanner:
    """Planner selecting discriminating experiments with the highest diagnostic value to falsify competing hypotheses."""

    @staticmethod
    def plan_next_best_experiment(hypotheses: List[HypothesisObject]) -> Optional[DiagnosticExperiment]:
        if not hypotheses:
            return None

        families = {h.root_cause_family for h in hypotheses if h.status != "FALSIFIED"}

        # 1. Separate LLMForge Adapter/Integration Failure from Model Failure
        if RootCauseFamily.LLMFORGE_INTEGRATION in families and (RootCauseFamily.DATA_CORPUS in families or RootCauseFamily.CONTEXT_SYSTEM in families):
            return DiagnosticExperiment(
                experiment_id="exp_01_adapter_vs_runtime",
                title="Adapter vs. Direct Runtime Comparison Test",
                target_hypotheses=[h.hypothesis_id for h in hypotheses],
                comparison_type="ADAPTER_VS_DIRECT_RUNTIME",
                description="Executes identical multi-turn recall prompt directly against local runtime vs via LLMForge CLI adapter.",
                diagnostic_value_score=0.98,
                required_resources=["local_runtime_endpoint"]
            )

        # 2. Separate Chat Template Failure from Model Capability Gap
        if RootCauseFamily.CHAT_TEMPLATE in families or RootCauseFamily.INFERENCE_GENERATION in families:
            return DiagnosticExperiment(
                experiment_id="exp_02_raw_vs_chat",
                title="Raw Completion vs. Chat Template Formatting Comparison",
                target_hypotheses=[h.hypothesis_id for h in hypotheses],
                comparison_type="RAW_VS_CHAT_MODE",
                description="Executes prompt with raw text completion formatting vs with chat template role tokens.",
                diagnostic_value_score=0.92,
                required_resources=["chat_template_config"]
            )

        # 3. Default discriminating experiment
        return DiagnosticExperiment(
            experiment_id="exp_03_short_vs_long",
            title="Short Context vs. Long Context Retrieval Comparison",
            target_hypotheses=[h.hypothesis_id for h in hypotheses],
            comparison_type="SHORT_VS_LONG_CONTEXT",
            description="Executes retrieval prompt with 500 token context vs 4000 token context.",
            diagnostic_value_score=0.85
        )
