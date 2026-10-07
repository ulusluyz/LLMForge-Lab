import os
import pytest
from llmforge.review.registry import LabelRegistry, LabelDefinition
from llmforge.review.store import HumanFeedbackStore, HumanReviewRecord, PassageAnnotation

def test_label_registry_and_passage_store(tmp_path):
    # 1. Test Label Registry
    registry = LabelRegistry.get_default_registry()
    assert "ADVERTISEMENT" in registry.labels
    assert "PROPAGANDA_SUSPECTED" in registry.labels

    adv_label = registry.get_label("ADVERTISEMENT")
    assert adv_label.default_action == "REJECT"
    assert len(adv_label.counter_examples) >= 1

    # 2. Test Passage-level Annotation & HumanFeedbackStore
    store = HumanFeedbackStore(str(tmp_path))
    doc_text = "Tarafımızca üretilen ürünler mükemmeldir. İndirimli satın almak için tıklayın! Haber bülteni burada biter."

    passage = PassageAnnotation(
        passage_id="p1",
        start_offset=42,
        end_offset=83,
        selected_text="İndirimli satın almak için tıklayın!",
        labels=["ADVERTISEMENT"],
        reason="Direct commercial CTA"
    )

    record = HumanReviewRecord(
        review_id="rev_test_001",
        document_id="doc_test_001",
        document_text=doc_text,
        decision="REJECT",
        labels=["ADVERTISEMENT", "COMMERCIAL_SPAM"],
        passage_annotations=[passage],
        reviewer_note="Passage 42-83 is direct advertisement",
        is_correction=True,
        correction_type="FALSE_POSITIVE"
    )

    store.save_record(record)
    loaded = store.load_all_records()

    assert len(loaded) == 1
    assert loaded[0].review_id == "rev_test_001"
    assert loaded[0].passage_annotations[0].start_offset == 42
    assert loaded[0].passage_annotations[0].selected_text == "İndirimli satın almak için tıklayın!"
    assert "COMMERCIAL_SPAM" in loaded[0].labels

    # 3. Backup & Import Test
    backup_path = tmp_path / "backup.jsonl"
    store.export_backup(str(backup_path))

    store2 = HumanFeedbackStore(str(tmp_path / "store2"))
    count = store2.import_backup(str(backup_path))
    assert count == 1
    assert len(store2.load_all_records()) == 1
