# LLMForge Lab Architecture

## Core Philosophy: The Maze and The Intelligence

LLMForge Lab enforces a strict separation between application control and intelligence reasoning:

```
+-------------------------------------------------------------------+
|                        PROGRAM (THE MAZE)                         |
|  State Machine | Process Lifecycle | Safety | Audits | Pipelines  |
+-------------------------------------------------------------------+
                                  ^
                                  | Reasoning & Evaluation
                                  v
+-------------------------------------------------------------------+
|                      INTELLIGENCE API LAYER                       |
|   Question Generation | Analysis | Hypotheses | Root Cause        |
+-------------------------------------------------------------------+
```

## System Workflow

1. **Preflight Audit:** Environment check (Local LLM accessibility, API provider status, disk space, storage write permissions).
2. **Local Model Inspection:** Query model metadata or record `UNKNOWN` for non-accessible properties.
3. **Adaptive Diagnostic Run:** 20-50 dynamic conversation turns over a hidden dependency graph.
4. **Hypothesis & Counter-Hypothesis Testing:** Flaws trigger counter-tests to verify failure causes.
5. **Root Cause Isolation:** Distinguishes model weight/context/tokenizer flaws from LLMForge system/prompt flaws.
6. **Data Requirement & Source Research:** Formulates token/domain data specifications and audits web sources.
7. **Corpus Pipeline V3:** Normalizes, deduplicates (exact SHA-256), writes durable build checkpoints, and exports manifests.
8. **Human Review:** UI at `http://127.0.0.1:8080/review` for human adjudication.
9. **Final Audit:** Verifies run completeness and signs outputs with SHA-256 hash signatures.
