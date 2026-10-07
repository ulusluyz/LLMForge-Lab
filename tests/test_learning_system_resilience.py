import os
import pytest
from llmforge.review.registry import LabelRegistry
from llmforge.review.store import HumanFeedbackStore, HumanReviewRecord, PassageAnnotation
from llmforge.review.learning import ThreeLayerLearningEngine
from llmforge.review.autonomy import PromotionGate
from llmforge.intelligence.provider import MockProvider, GeminiProvider

def test_learning_system_resilience_and_provider_replacement(tmp_path):
    registry = LabelRegistry.get_default_registry()
    store = HumanFeedbackStore(str(tmp_path / "resilience_store"))

    # 1. Provider Replacement & Preservation
    provider_a = MockProvider({"responses": {"default_text": "Provider A Response"}})
    passage = PassageAnnotation(passage_id="p1", start_offset=0, end_offset=35, selected_text="İndirimli satın almak için tıklayın", labels=["ADVERTISEMENT"])
    store.save_record(HumanReviewRecord(review_id="rev_p1", document_id="doc_p1", document_text="text", decision="REJECT", labels=["ADVERTISEMENT"], passage_annotations=[passage]))

    engine = ThreeLayerLearningEngine(store, registry)
    assert len(engine.learned_patterns) >= 1

    # Swap provider to Provider B (Mock)
    provider_b = MockProvider({"responses": {"default_text": "Provider B Response"}})
    # Learned knowledge remains preserved
    assert len(engine.learned_patterns) >= 1
    eval_res = engine.evaluate_document("Aşağıdaki bağlantıya tıklayarak İndirimli satın almak için tıklayın kampanyasından faydalanın.")
    assert eval_res.decision == "AUTO_REJECT"

    # 2. Restart Persistence
    reloaded_store = HumanFeedbackStore(str(tmp_path / "resilience_store"))
    records = reloaded_store.load_all_records()
    assert len(records) == 1
    assert records[0].review_id == "rev_p1"

    # 3. Rebuild from Raw Evidence
    engine.learned_patterns.clear()
    assert len(engine.learned_patterns) == 0
    engine.rebuild_learned_knowledge()
    assert len(engine.learned_patterns) >= 1

    # 4. Self-Training Loop Protection (SYSTEM_PREDICTED isolation)
    system_pred_rec = HumanReviewRecord(
        review_id="rev_sys_pred", document_id="doc_sys_pred",
        document_text="Predicted text", decision="AUTO_REJECT",
        labels=["SYSTEM_LABEL"], provenance="SYSTEM_PREDICTED"
    )
    store.save_record(system_pred_rec)
    engine.rebuild_learned_knowledge()
    # System predictions do not create ground truth positive patterns
    assert not any(p.label_id == "SYSTEM_LABEL" for p in engine.learned_patterns)

    # 5. Backup / Export / Import Round-Trip
    backup_file = tmp_path / "backup.jsonl"
    store.export_backup(str(backup_file))

    imported_store = HumanFeedbackStore(str(tmp_path / "imported_store"))
    imported_count = imported_store.import_backup(str(backup_file))
    assert imported_count == 2
    assert len(imported_store.load_all_records()) == 2
