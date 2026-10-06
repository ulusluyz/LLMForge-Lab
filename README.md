# LLMForge Lab

> **Autonomous LLM Diagnostic, Audit & Corpus Engineering Laboratory**

LLMForge Lab is an autonomous laboratory system that evaluates local large language models (LLMs) through dynamic and adaptive experiments. It investigates root causes with evidence, distinguishes model/architecture/runtime/tokenizer/context/training/data issues, identifies data requirements, searches for genuine web sources, and prepares audit-checked training corpora using Pipeline V3.

---

## Architecture Blueprint

**Principle:**
- **Program = The Maze.** Enforces state machine, CLI/process boundaries, schema, security limits, audits, human review, and pipeline execution.
- **LLM API = The Intelligence Layer.** Generates dynamic questions, evaluates responses, hypothesizes, creates counter-tests, and formulates root-cause candidates.

```text
GÖZLEM → KANIT → HİPOTEZ → KARŞI HİPOTEZ → KONTROLLÜ DENEY → KÖK NEDEN → ÇÖZÜM İHTİYACI → VERİ İHTİYACI → KAYNAK ARAŞTIRMASI → CORPUS PIPELINE V3 → AUDIT → HUMAN REVIEW → DOĞRULANMIŞ CORPUS
```

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
- **Human Review UI:** `http://127.0.0.1:8080/review`

### Running an Autonomous Diagnostic Evaluation

```bash
llmforge run --run-id run_001 --max-turns 20
```

---

## Subsystems Overview

### 1. Local LLM Adapters
Supports:
- Direct CLI Subprocess (`SubprocessCLIAdapter`)
- Generic OpenAI-compatible Local HTTP (`GenericHTTPAdapter`)
- Ollama (`OllamaAdapter`)
- llama.cpp Server (`LlamaCppAdapter`)
- vLLM (`VLLMAdapter`)

### 2. Multi-Turn Adaptive Diagnostic Engine & Hidden Graph
Executes 20–50 turn adaptive evaluations using a hidden dependency graph containing edges (`RECALL`, `REFERENCE`, `CONTRADICTION`, `COUNTER_TEST`, `DISTRACTOR`). Extracts multi-objective diagnostic signals per turn.

### 3. Data Requirement & Pipeline V3
- Generates precise, justified Data Requirement Specifications.
- Discovers web sources with Source Audits (`ACCEPT`, `HUMAN_REVIEW`, `REJECT`).
- Executes Pipeline V3 (streaming, normalization, exact SHA-256 dedup, durable checkpoints, immutable manifests).

### 4. Human Review Web UI
Interactive workspace at `http://127.0.0.1:8080/review` displaying categorizations ("Lisans Belirsiz", "Sentetik İçerik Şüphesi"), batch actions, and reviewer decision history.

### 5. Audit Subsystem
Includes 11 structured audit modules with SHA-256 hash-chained tamper protection.

---

## Documentation & Validation

Detailed documentation available in `docs/`:
- `ARCHITECTURE.md`
- `DIAGNOSTIC_ENGINE.md`
- `AUDIT_SYSTEM.md`
- `PIPELINE_V3.md`
- `HUMAN_REVIEW.md`

### Test Validation Matrix Summary

| Test Name | Level | Type | Status |
|---|---|---|---|
| Local Subprocess CLI Adapter Execution | Level C — Local E2E | Local Real Process | PASS |
| Mock Intelligence API Provider | Level A — Unit | Mock | PASS |
| Real Gemini Intelligence API Provider | Level D — Real External | Real API | NOT_RUN |
| Multi-Turn Adaptive Diagnostic Engine & Hidden Graph | Level B — Integration | Local Process + Mock | PASS |
| Corpus Pipeline V3 Deduplication & Checkpoint Resume | Level B — Integration | Local File System | PASS |
| Audit Subsystem & Hash-Chained Tamper Protection | Level A — Unit | Local Real | PASS |
| FastAPI Web Dashboard & Human Review UI | Level B — Integration | Local HTTP Endpoint | PASS |

---

## License

[Apache License 2.0](LICENSE)
