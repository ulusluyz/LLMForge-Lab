# LLMForge Lab

> **Autonomous LLM Diagnostic, Audit, Corpus Engineering & Human Review Intelligence Laboratory**

LLMForge Lab is an autonomous laboratory system that evaluates local large language models (LLMs) through dynamic multi-turn experiments, isolates root causes with evidence, searches web sources, prepares audit-checked training corpora via Pipeline V3, and continually learns from human feedback through a provider-independent Human Review Intelligence System.

---

## Key Capabilities

1. **Maze vs. Intelligence Principle:** Program controls state machine, process lifecycles, and security limits; Reasoning API acts as the adaptive intelligence layer.
2. **Multi-Turn Diagnostic Engine & Hidden Test Graph:** Dynamically generates multi-turn Turkish evaluation questions with hidden dependency graphs (`RECALL`, `COUNTER_TEST`) and multi-objective signal extraction.
3. **System-vs-Model Fault Isolation:** Distinguishes model context weaknesses from LLMForge Lab history forwarding failures.
4. **Corpus Pipeline V3:** Ingests, normalizes, deduplicates via MinHash signature vectors & Jaccard candidate verification, saves durable build checkpoints (`checkpoint.json`), and enforces 80/10/10 cluster split isolation.
5. **11 Signed Audit Modules:** Executes Preflight, Runtime, Diagnostic, Source, Pipeline, Corpus Quality, Human Review, Human Feedback Learning, Reproducibility, Security, Regression, and Final Audits signed with SHA-256 hash signatures.
6. **Human Review Intelligence & Active Learning:**
   - Provider-independent storage (`HumanFeedbackStore`, `LabelRegistry`).
   - Passage-level character offset span annotations `[start, end]`.
   - Three-layer learning architecture (Raw Evidence -> Learned Patterns -> Decision Logic).
   - Progressive autonomy modes (`MANUAL`, `SHADOW`, `ASSISTED`, `AUTONOMOUS`) with Golden Set promotion gates (`PromotionGate`).
7. **Production Security Hardening:** Canonical path sandboxing, SSRF loopback/private IP blocking, `SecretRedactor` key scrubbing, prompt injection sanitization, zip bomb limits, API call budget caps, and tool allowlists.

---

## Quick Start

### Installation

Requires Python 3.12+

```bash
git clone https://github.com/user/llmforge-lab.git
cd llmforge-lab
pip install -e ".[dev]"
```

### Starting the Server & Web GUI Dashboard

```bash
llmforge serve --host 127.0.0.1 --port 8080
```

- **Dashboard:** `http://127.0.0.1:8080/`
- **Human Review Workspace:** `http://127.0.0.1:8080/review`

### Running an Autonomous Diagnostic Evaluation

```bash
llmforge run --run-id run_001 --max-turns 20
```

---

## Documentation Index

Detailed technical documentation available in `docs/`:
- `ARCHITECTURE.md`
- `DIAGNOSTIC_ENGINE.md`
- `HUMAN_FEEDBACK_LEARNING.md`
- `HUMAN_REVIEW_TAXONOMY_RESEARCH.md`
- `AUDIT_SYSTEM.md`
- `PIPELINE_V3.md`
- `HUMAN_REVIEW.md`
- `SECURITY_ARCHITECTURE.md`
- `SECURITY_VALIDATION_REPORT.md`
- `REQUIREMENTS_AUDIT.md`
- `FINAL_VALIDATION_REPORT.md`

---

## License

[Apache License 2.0](LICENSE)
