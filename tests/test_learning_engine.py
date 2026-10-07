import os
import pytest
from llmforge.review.registry import LabelRegistry
from llmforge.review.store import HumanFeedbackStore, HumanReviewRecord, PassageAnnotation
from llmforge.review.learning import ThreeLayerLearningEngine

def test_three_layer_learning_and_active_learning(tmp_path):
    registry = LabelRegistry.get_default_registry()
    store = HumanFeedbackStore(str(tmp_path))

    # Phase 1: Record initial human review feedback
    passage = PassageAnnotation(
        passage_id="p1",
        start_offset=0,
        end_offset=35,
        selected_text="İndirimli satın almak için tıklayın",
        labels=["ADVERTISEMENT"]
    )
    rec = HumanReviewRecord(
        review_id="rev_01",
        document_id="doc_01",
        document_text="İndirimli satın almak için tıklayın!",
        decision="REJECT",
        labels=["ADVERTISEMENT"],
        passage_annotations=[passage],
        is_correction=True
    )
    store.save_record(rec)

    # Phase 2: Instantiate Three-Layer Learning Engine and evaluate new records
    engine = ThreeLayerLearningEngine(store, registry)
    assert len(engine.learned_patterns) >= 1

    # Evaluate document containing learned advertisement pattern
    res1 = engine.evaluate_document("Aşağıdaki bağlantıya tıklayarak İndirimli satın almak için tıklayın kampanyasından faydalanın.")
    assert res1.decision == "AUTO_REJECT"
    assert "ADVERTISEMENT" in res1.assigned_labels

    # Evaluate counter-example document (neutral review mentioning counter-phrase)
    counter_text = "Ürünü iki hafta inceledik; tarafsız artı ve eksi yönleri şunlardır. İndirimli satın almak için tıklayın"
    res2 = engine.evaluate_document(counter_text)
    assert res2.decision == "HUMAN_REVIEW"
    assert "Conflicting positive and counter-examples" in res2.escalation_reason
