# Pipeline V3 Specification

Corpus Pipeline V3 extends Pipeline V2 with durable build checkpoints, streaming deduplication, and source provenance tracking.

## Core Pipeline V3 Capabilities

1. **Streaming & Normalization:** Strips malformed control characters, normalizes whitespace, and filters records below minimum length thresholds.
2. **Exact SHA-256 Deduplication:** Computes strict text hashes to eliminate exact duplicates across shards.
3. **Durable Build Checkpoint (`--resume`):** Periodically writes `checkpoint.json` recording processed hash sets and stage status. Interrupted pipeline builds can resume seamlessly.
4. **Split Isolation & Contamination Check:** Isolates train/validation/test splits at the cluster level to prevent data leakage.
5. **Immutable SHA-256 Manifest:** Generates `manifest.json` containing total raw record count, accepted record count, and artifact SHA-256 hash digests.
