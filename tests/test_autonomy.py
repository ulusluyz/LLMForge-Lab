import pytest
from llmforge.review.registry import LabelRegistry
from llmforge.review.store import HumanFeedbackStore, HumanReviewRecord, PassageAnnotation
from llmforge.review.learning import ThreeLayerLearningEngine
from llmforge.review.autonomy import PromotionGate

def test_promotion_gate_and_golden_validation(tmp_path):
    registry = LabelRegistry.get_default_registry()
    store1 = HumanFeedbackStore(str(tmp_path / "store1"))
    store2 = HumanFeedbackStore(str(tmp_path / "store2"))

    # Golden Set Document
    golden_record = HumanReviewRecord(
        review_id="golden_01",
        document_id="doc_g01",
        document_text="İndirimli satın almak için tıklayın kampanyası başlamıştır.",
        decision="REJECT",
        labels=["ADVERTISEMENT"]
    )

    golden_set = [golden_record]

    # Current Engine trained on advertisement passage
    passage = PassageAnnotation(passage_id="p1", start_offset=0, end_offset=35, selected_text="İndirimli satın almak için tıklayın", labels=["ADVERTISEMENT"])
    store1.save_record(HumanReviewRecord(review_id="rev_1", document_id="doc_1", document_text="text", decision="REJECT", labels=["ADVERTISEMENT"], passage_annotations=[passage]))
    curr_engine = ThreeLayerLearningEngine(store1, registry)

    # Candidate Engine trained on different store
    store2.save_record(HumanReviewRecord(review_id="rev_2", document_id="doc_2", document_text="text", decision="REJECT", labels=["ADVERTISEMENT"], passage_annotations=[passage]))
    cand_engine = ThreeLayerLearningEngine(store2, registry)

    gate = PromotionGate(golden_set)
    res = gate.evaluate_candidate_policy(curr_engine, cand_engine, min_accuracy_threshold=0.80)

    assert res.promoted is True
    assert res.candidate_accuracy >= 0.80
