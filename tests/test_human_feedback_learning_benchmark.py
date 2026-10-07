import os
import pytest
from llmforge.review.registry import LabelRegistry
from llmforge.review.store import HumanFeedbackStore
from llmforge.review.learning import ThreeLayerLearningEngine
from llmforge.review.benchmark_generator import BenchmarkDatasetGenerator

def test_large_scale_learning_curve_and_active_learning_benchmark(tmp_path):
    registry = LabelRegistry.get_default_registry()
    training_feedback, unseen_validation = BenchmarkDatasetGenerator.generate_benchmark_corpus(count=1000, seed=42)

    assert len(training_feedback) == 500
    assert len(unseen_validation) == 500

    checkpoints = [0, 50, 100, 250, 500]
    learning_curve_results = []

    for checkpoint in checkpoints:
        store_dir = tmp_path / f"store_ckpt_{checkpoint}"
        store = HumanFeedbackStore(str(store_dir))

        # Ingest checkpoint slice of training feedback
        for rec in training_feedback[:checkpoint]:
            store.save_record(rec)

        engine = ThreeLayerLearningEngine(store, registry)

        # Evaluate on Unseen Validation Corpus (500 records)
        val_results = [engine.evaluate_document(rec.document_text) for rec in unseen_validation]

        auto_decisions = [res for res in val_results if res.decision in ["AUTO_ACCEPT", "AUTO_REJECT"]]
        human_reviews = [res for res in val_results if res.decision == "HUMAN_REVIEW"]

        # Calculate accuracy on auto-decided subset (Selective Accuracy)
        correct_auto = 0
        for rec, res in zip(unseen_validation, val_results):
            if res.decision == "AUTO_REJECT" and rec.decision == "REJECT":
                correct_auto += 1
            elif res.decision == "AUTO_ACCEPT" and rec.decision == "ACCEPT":
                correct_auto += 1

        selective_accuracy = round(correct_auto / len(auto_decisions), 4) if auto_decisions else 1.0
        coverage = round(len(auto_decisions) / len(unseen_validation), 4)
        human_review_rate = round(len(human_reviews) / len(unseen_validation), 4)

        learning_curve_results.append({
            "checkpoint": checkpoint,
            "coverage": coverage,
            "human_review_rate": human_review_rate,
            "selective_accuracy": selective_accuracy
        })

    # Assertions for Learning Curve Progression
    ckpt_0 = learning_curve_results[0]
    ckpt_500 = learning_curve_results[-1]

    # As verified feedback increases, auto coverage increases and human review rate decreases
    assert ckpt_500["coverage"] > ckpt_0["coverage"]
    assert ckpt_500["human_review_rate"] < ckpt_0["human_review_rate"]
    # Selective accuracy remains high (quality preserved)
    assert ckpt_500["selective_accuracy"] >= 0.85
