import os
import json
import pytest
from llmforge.review.registry import LabelRegistry
from llmforge.review.store import HumanFeedbackStore, HumanReviewRecord, PassageAnnotation
from llmforge.review.learning import ThreeLayerLearningEngine

def test_controlled_6_round_learning_experiment(tmp_path):
    registry = LabelRegistry.get_default_registry()
    store = HumanFeedbackStore(str(tmp_path))
    engine = ThreeLayerLearningEngine(store, registry)

    # ==========================================
    # ROUND 0 — BASELINE (Unseen Validation Corpus)
    # ==========================================
    eval_docs = [
        "Aşağıdaki bağlantıya tıklayarak İndirimli satın almak için tıklayın kampanyasından faydalanın.",
        "Ürünü iki hafta inceledik; tarafsız artı ve eksi yönleri şunlardır.",
        "Türkiye'nin başkenti Ankara şehridir.",
        "Doğruları yalnızca tarafımız söyler, diğer tüm kaynaklar haindir."
    ]

    r0_results = [engine.evaluate_document(doc) for doc in eval_docs]
    r0_human_review_count = sum(1 for res in r0_results if res.decision == "HUMAN_REVIEW")
    r0_auto_count = sum(1 for res in r0_results if res.decision in ["AUTO_ACCEPT", "AUTO_REJECT"])

    assert r0_auto_count + r0_human_review_count == 4

    # ==========================================
    # ROUND 1 — HUMAN FEEDBACK INGESTION
    # ==========================================
    passage_adv = PassageAnnotation(passage_id="p_adv", start_offset=0, end_offset=35, selected_text="İndirimli satın almak için tıklayın", labels=["ADVERTISEMENT"])
    fb_adv = HumanReviewRecord(
        review_id="rev_r1_adv", document_id="doc_r1_adv",
        document_text="İndirimli satın almak için tıklayın!",
        decision="REJECT", labels=["ADVERTISEMENT"],
        passage_annotations=[passage_adv], is_correction=True
    )
    store.save_record(fb_adv)

    passage_prop = PassageAnnotation(passage_id="p_prop", start_offset=0, end_offset=38, selected_text="Doğruları yalnızca tarafımız söyler", labels=["PROPAGANDA_SUSPECTED"])
    fb_prop = HumanReviewRecord(
        review_id="rev_r1_prop", document_id="doc_r1_prop",
        document_text="Doğruları yalnızca tarafımız söyler!",
        decision="HUMAN_REVIEW", labels=["PROPAGANDA_SUSPECTED"],
        passage_annotations=[passage_prop], is_correction=True
    )
    store.save_record(fb_prop)

    engine.rebuild_learned_knowledge()
    assert len(engine.learned_patterns) >= 2

    # ==========================================
    # ROUND 2 — UNSEEN GENERALIZATION
    # ==========================================
    unseen_adv = "Aşağıdaki bağlantıya tıklayarak İndirimli satın almak için tıklayın fırsatını kaçırmayın."
    r2_res = engine.evaluate_document(unseen_adv)
    assert r2_res.decision == "AUTO_REJECT"
    assert "ADVERTISEMENT" in r2_res.assigned_labels

    # ==========================================
    # ROUND 3 — COUNTER-EXAMPLES & DISAMBIGUATION
    # ==========================================
    counter_doc = "Ürünü iki hafta inceledik; tarafsız artı ve eksi yönleri şunlardır. İndirimli satın almak için tıklayın"
    r3_res = engine.evaluate_document(counter_doc)
    assert r3_res.decision == "HUMAN_REVIEW"
    assert "Conflicting positive and counter-examples" in r3_res.escalation_reason

    # ==========================================
    # ROUND 4 — HIGH-RISK LABEL ESCALATION
    # ==========================================
    propaganda_doc = "Doğruları yalnızca tarafımız söyler, diğer kurumların hiçbiri gerçekleri açıklayamaz."
    r4_res = engine.evaluate_document(propaganda_doc)
    assert r4_res.decision == "HUMAN_REVIEW"
    assert "PROPAGANDA_SUSPECTED" in r4_res.assigned_labels
    assert "High-Risk Label" in r4_res.escalation_reason

    # ==========================================
    # ROUND 5 — NEW DOMAIN LEARNING & ADAPTATION
    # ==========================================
    novel_doc = "Kuantum renk dinamiği ve kuark çeşnileri simetrisi yüksek enerji fiziğinin temel konularındandır."
    fb_novel = HumanReviewRecord(
        review_id="rev_r5_novel", document_id="doc_r5_novel",
        document_text=novel_doc, decision="ACCEPT", labels=["PHYSICS_DOMAIN"],
        passage_annotations=[], is_correction=False
    )
    store.save_record(fb_novel)
    engine.rebuild_learned_knowledge()

    r5_res = engine.evaluate_document(novel_doc)
    assert r5_res.decision in ["AUTO_ACCEPT", "HUMAN_REVIEW"]
