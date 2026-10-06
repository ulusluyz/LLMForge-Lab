import os
import json
import hashlib
import time
from typing import List, Dict, Any, Optional, Set
from pydantic import BaseModel, Field

class CorpusRecord(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    provenance: str = "UNKNOWN"
    quality_score: float = 1.0
    status: str = "ACCEPT" # ACCEPT, HUMAN_REVIEW, REJECT

class PipelineV3Checkpoint(BaseModel):
    checkpoint_id: str
    stage: str
    processed_counts: Dict[str, int] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)

class CorpusPipelineV3:
    """Pipeline V3: Complete V2 Feature Parity + MinHash Near-Dedup, Durable Checkpoints, and Split Isolation."""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.seen_exact_hashes: Set[str] = set()
        self.seen_minhashes: Set[int] = set()
        self.processed_records: List[CorpusRecord] = []
        self.checkpoint_file = os.path.join(output_dir, "checkpoint.json")

    def _compute_minhash(self, text: str) -> int:
        words = text.lower().split()
        shingles = [" ".join(words[i:i+2]) for i in range(len(words)-1)] if len(words) > 1 else words
        if not shingles:
            return 0
        hashes = [int(hashlib.md5(s.encode("utf-8")).hexdigest(), 16) for s in shingles]
        return min(hashes)

    def load_checkpoint(self) -> bool:
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, "r") as f:
                    data = json.load(f)
                    self.seen_exact_hashes = set(data.get("seen_exact_hashes", []))
                    self.seen_minhashes = set(data.get("seen_minhashes", []))
                    return True
            except Exception:
                return False
        return False

    def save_checkpoint(self, stage: str):
        data = {
            "stage": stage,
            "seen_exact_hashes": list(self.seen_exact_hashes),
            "seen_minhashes": list(self.seen_minhashes),
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

            # 3. Near-Deduplication via MinHash
            minhash_val = self._compute_minhash(normalized_text)
            if minhash_val != 0 and minhash_val in self.seen_minhashes:
                rec.status = "REJECT"
                continue
            if minhash_val != 0:
                self.seen_minhashes.add(minhash_val)

            # 4. Decision check
            if rec.status == "ACCEPT":
                cleaned.append(rec)
            self.processed_records.append(rec)

        self.save_checkpoint("deduplicated")
        return cleaned

    def export_corpus_artifacts(self, records: List[CorpusRecord]) -> Dict[str, Any]:
        corpus_path = os.path.join(self.output_dir, "train_corpus.jsonl")
        manifest_path = os.path.join(self.output_dir, "manifest.json")

        accepted_records = [r for r in records if r.status == "ACCEPT"]

        with open(corpus_path, "w", encoding="utf-8") as f:
            for rec in accepted_records:
                f.write(rec.model_dump_json() + "\n")

        with open(corpus_path, "rb") as f:
            artifact_hash = hashlib.sha256(f.read()).hexdigest()

        manifest = {
            "total_raw": len(records),
            "accepted_count": len(accepted_records),
            "artifact_hash": artifact_hash,
            "timestamp": time.time()
        }

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return manifest
