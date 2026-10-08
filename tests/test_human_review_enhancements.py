import pytest
from llmforge.review.schemas import QualityReviewSchema
from llmforge.review.agreement import AIHumanAgreementTracker, AIHumanComparisonRecord
from llmforge.review.discovery import TaxonomyDiscoveryEngine
from llmforge.review.diff import DocumentDiffEngine, SafeCleanupGuard
from llmforge.review.shadow import ShadowAuditSampler
from llmforge.review.store import HumanFeedbackStore, HumanReviewRecord

def test_document_diff_and_safe_cleanup():
    orig = "Kaliteli haber makalesi.\nTelefon: 0532 111 22 33\nSon bölüm."
    edit = "Kaliteli haber makalesi.\nSon bölüm."

    diff_res = DocumentDiffEngine.compute_diff(orig, edit)
    assert len(diff_res.diff_ops) > 0
    assert "PHONE_NUMBER_PATTERN" in diff_res.detected_structural_patterns

    guard_res = SafeCleanupGuard.classify_correction(orig, edit)
    assert guard_res["safety_class"] == "SAFE_DETERMINISTIC"
    assert guard_res["is_auto_cleanable"] is True

def test_ai_human_agreement_tracker(tmp_path):
    filepath = str(tmp_path / "agreement.jsonl")
    tracker = AIHumanAgreementTracker(filepath)

    rec = AIHumanComparisonRecord(
        item_id="item_01",
        provider_name="GeminiProvider",
        ai_decision="ACCEPT",
        human_decision="ACCEPT",
        ai_labels=["NATURAL_TURKISH"],
        human_labels=["NATURAL_TURKISH"],
        decision_matches=True,
        label_overlap_count=1
    )
    tracker.record_comparison(rec)

    metrics = tracker.compute_metrics()
    assert metrics["total_comparisons"] == 1
    assert metrics["decision_agreement_rate"] == 1.0

def test_taxonomy_discovery_engine(tmp_path):
    store_dir = str(tmp_path / "feedback_store")
    store = HumanFeedbackStore(store_dir)

    r1 = HumanReviewRecord(
        review_id="rev_1",
        document_id="doc_1",
        document_text="Text 1",
        decision="REJECT",
        reviewer_note="Aynı fikir farklı kelimelerle tekrar edilmiş."
    )
    r2 = HumanReviewRecord(
        review_id="rev_2",
        document_id="doc_2",
        document_text="Text 2",
        decision="REJECT",
        reviewer_note="Metin semantik olarak tekrar içeriyor."
    )
    store.save_record(r1)
    store.save_record(r2)

    discovery = TaxonomyDiscoveryEngine(store)
    candidates = discovery.discover_candidates(min_frequency=2)
    assert len(candidates) > 0
    assert candidates[0].proposed_label_name == "SEMANTIC_REPETITION"

def test_shadow_audit_sampler(tmp_path):
    filepath = str(tmp_path / "shadow.jsonl")
    sampler = ShadowAuditSampler(sample_rate=1.0, storage_filepath=filepath)

    sample = sampler.record_sample("item_100", "AUTO_ACCEPT", ["NATURAL_TURKISH"])
    assert sample.item_id == "item_100"
    assert sampler.get_disagreement_rate() == 0.0
