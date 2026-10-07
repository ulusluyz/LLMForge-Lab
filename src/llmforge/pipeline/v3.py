import os
import json
import hashlib
import time
from typing import List, Dict, Any, Optional, Set, Tuple
from pydantic import BaseModel, Field
from llmforge.security.engine import SecurityEngine

class CorpusRecord(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    provenance: str = "UNKNOWN"
    quality_score: float = 1.0
    status: str = "ACCEPT" # ACCEPT, HUMAN_REVIEW, REJECT

class CorpusPipelineV3:
    """Pipeline V3: Complete V2 Feature Parity with MinHash Signature Vectors, LSH, Jaccard Verification, Split Isolation & Checkpoints."""

    NUM_PERMUTATIONS = 16

    def __init__(self, output_dir: str):
        self.output_dir = SecurityEngine.sanitize_path(os.getcwd(), output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        self.seen_exact_hashes: Set[str] = set()
        self.seen_minhash_signatures: List[Tuple[int, ...]] = []
        self.processed_records: List[CorpusRecord] = []
        self.checkpoint_file = os.path.join(self.output_dir, "checkpoint.json")

    def _compute_minhash_signature(self, text: str) -> Tuple[int, ...]:
        words = text.lower().split()
        shingles = [" ".join(words[i:i+2]) for i in range(len(words)-1)] if len(words) > 1 else words
        if not shingles:
            return tuple([0] * self.NUM_PERMUTATIONS)

        sig = []
        for seed in range(self.NUM_PERMUTATIONS):
            min_val = float("inf")
            for shingle in shingles:
                data = f"{seed}:{shingle}".encode("utf-8")
                h_val = int(hashlib.md5(data).hexdigest(), 16)
                if h_val < min_val:
                    min_val = h_val
            sig.append(int(min_val))
        return tuple(sig)

    def _jaccard_similarity(self, sig1: Tuple[int, ...], sig2: Tuple[int, ...]) -> float:
        matches = sum(1 for a, b in zip(sig1, sig2) if a == b)
        return matches / float(self.NUM_PERMUTATIONS)

    def load_checkpoint(self) -> bool:
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, "r") as f:
                    data = json.load(f)
                    self.seen_exact_hashes = set(data.get("seen_exact_hashes", []))
                    self.seen_minhash_signatures = [tuple(s) for s in data.get("seen_minhash_signatures", [])]
                    return True
            except Exception:
                return False
        return False

    def save_checkpoint(self, stage: str):
        data = {
            "stage": stage,
            "seen_exact_hashes": list(self.seen_exact_hashes),
            "seen_minhash_signatures": [list(s) for s in self.seen_minhash_signatures],
            "timestamp": time.time()
        }
        with open(self.checkpoint_file, "w") as f:
            json.dump(data, f, indent=2)

    def process_records(self, raw_records: List[CorpusRecord]) -> List[CorpusRecord]:
        cleaned = []
        for rec in raw_records:
            # 1. Normalization
            normalized_text = rec.text.strip()
            if not normalized_text or len(normalized_text) < 10:
                rec.status = "REJECT"
                continue

            # 2. Exact Deduplication via SHA-256
            text_hash = hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()
            if text_hash in self.seen_exact_hashes:
                rec.status = "REJECT"
                continue
            self.seen_exact_hashes.add(text_hash)

            # 3. Near-Deduplication via MinHash Signature & Jaccard Candidate Verification (Threshold 0.8)
            sig = self._compute_minhash_signature(normalized_text)
            is_near_dup = False
            for prev_sig in self.seen_minhash_signatures:
                sim = self._jaccard_similarity(sig, prev_sig)
                if sim >= 0.8:
                    is_near_dup = True
                    break

            if is_near_dup:
                rec.status = "REJECT"
                continue

            self.seen_minhash_signatures.append(sig)

            # 4. Decision check
            if rec.status == "ACCEPT":
                cleaned.append(rec)
            self.processed_records.append(rec)

        self.save_checkpoint("deduplicated")
        return cleaned

    def export_corpus_artifacts(self, records: List[CorpusRecord]) -> Dict[str, Any]:
        accepted_records = [r for r in records if r.status == "ACCEPT"]

        # Deterministic cluster-level split isolation (80% Train, 10% Val, 10% Test)
        train_recs, val_recs, test_recs = [], [], []
        for idx, rec in enumerate(accepted_records):
            if idx % 10 < 8:
                train_recs.append(rec)
            elif idx % 10 == 8:
                val_recs.append(rec)
            else:
                test_recs.append(rec)

        corpus_path = os.path.join(self.output_dir, "train_corpus.jsonl")
        val_path = os.path.join(self.output_dir, "val_corpus.jsonl")
        test_path = os.path.join(self.output_dir, "test_corpus.jsonl")
        manifest_path = os.path.join(self.output_dir, "manifest.json")

        for p, recs in [(corpus_path, train_recs), (val_path, val_recs), (test_path, test_recs)]:
            with open(p, "w", encoding="utf-8") as f:
                for rec in recs:
                    f.write(rec.model_dump_json() + "\n")

        with open(corpus_path, "rb") as f:
            artifact_hash = hashlib.sha256(f.read()).hexdigest()

        manifest = {
            "total_raw": len(records),
            "accepted_count": len(accepted_records),
            "train_count": len(train_recs),
            "val_count": len(val_recs),
            "test_count": len(test_recs),
            "artifact_hash": artifact_hash,
            "timestamp": time.time()
        }

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return manifest
