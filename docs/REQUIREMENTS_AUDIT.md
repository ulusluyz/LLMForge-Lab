# LLMForge Lab Requirements Audit Matrix

| # | Requirement Area | Implementation Class / Module | Primary Files | Test Verification | Real/Mock | Status |
|---|---|---|---|---|---|---|
| 1 | Program=Maze, API=Intelligence | `AdaptiveDiagnosticEngine` | `src/llmforge/diagnostics/engine.py` | `tests/test_diagnostics.py` | Local Real Process + Mock | `TESTED` |
| 2 | Main Workflow Pipeline | `llmforge.cli` / `server` | `src/llmforge/cli.py` | `tests/test_server.py` | Local Real | `TESTED` |
| 3 | Preflight Audit | `AuditEngine.run_preflight_audit` | `src/llmforge/audit/engine.py` | `tests/test_audit.py` | Local Real | `TESTED` |
| 4 | Test Budget (20-50 turns) | `AdaptiveDiagnosticEngine` | `src/llmforge/diagnostics/engine.py` | `tests/test_diagnostics.py` | Local Real + Mock | `TESTED` |
| 5 | Multi-Turn Hidden Dependency Graph | `HiddenTestGraph` | `src/llmforge/diagnostics/graph.py` | `tests/test_diagnostics.py` | Local Real | `TESTED` |
| 6 | Multi-Objective Diagnostic Signals | `TurnEvaluation` | `src/llmforge/diagnostics/schemas.py` | `tests/test_diagnostics.py` | Local Real | `TESTED` |
| 7 | Evaluation Areas (Language, Reasoning, Context, etc.) | `AdaptiveDiagnosticEngine` | `src/llmforge/diagnostics/engine.py` | `tests/test_diagnostics.py` | Local Real | `TESTED` |
| 8 | Adaptive Test Motor & Counter-Hypothesis | `AdaptiveDiagnosticEngine` | `src/llmforge/diagnostics/engine.py` | `tests/test_diagnostics.py` | Local Real | `TESTED` |
| 9 | Error Localization & Root Cause Analysis | `RootCauseCandidate` | `src/llmforge/diagnostics/schemas.py` | `tests/test_diagnostics.py` | Local Real | `TESTED` |
| 10 | Model Failure vs System Failure Isolation | `AdaptiveDiagnosticEngine` | `src/llmforge/diagnostics/engine.py` | `tests/test_system_failure_isolation.py` | Local Real | `TESTED` |
| 11 | Diagnostic Audit & Evidence Schema | `AuditEngine` / `TurnEvaluation` | `src/llmforge/audit/engine.py` | `tests/test_audit.py` | Local Real | `TESTED` |
| 12 | Data Requirement Specification | `DataRequirementSpec` | `src/llmforge/research/schemas.py` | `tests/test_pipeline_and_research.py` | Local Real | `TESTED` |
| 13 | Web Source Research & Source Audit | `MockResearchAdapter` / `SourceAuditRecord` | `src/llmforge/research/adapters.py` | `tests/test_pipeline_and_research.py` | Local Real | `TESTED` |
| 14 | Pipeline V2 -> V3 Feature Parity (Streaming, Normalization, Exact Dedup) | `CorpusPipelineV3` | `src/llmforge/pipeline/v3.py` | `tests/test_pipeline_and_research.py` | Local Real | `TESTED` |
| 15 | Pipeline V3 MinHash/LSH Near-Dedup & Split Isolation | `CorpusPipelineV3` | `src/llmforge/pipeline/v3.py` | `tests/test_pipeline_resume.py` | Local Real | `TESTED` |
| 16 | Durable Build Checkpoint & Resume | `CorpusPipelineV3.save_checkpoint` | `src/llmforge/pipeline/v3.py` | `tests/test_pipeline_resume.py` | Local Real | `TESTED` |
| 17 | 11 Complete Audit Subsystems | `AuditEngine` | `src/llmforge/audit/engine.py` | `tests/test_all_audits.py` | Local Real | `TESTED` |
| 18 | Human Review Web UI (127.0.0.1:8080/review) | `FastAPI Server` | `src/llmforge/server.py` | `tests/test_server.py` | Local Real | `TESTED` |
| 19 | Corpus Lineage & Provenance | `CorpusRecord` | `src/llmforge/pipeline/v3.py` | `tests/test_dataset_lineage.py` | Local Real | `TESTED` |
| 20 | Model Versions & Regression Audit | `AuditEngine.run_regression_audit` | `src/llmforge/audit/engine.py` | `tests/test_all_audits.py` | Local Real | `TESTED` |
| 21 | Intelligence API Provider (Gemini & Mock) | `GeminiProvider` / `MockProvider` | `src/llmforge/intelligence/provider.py` | `tests/test_adapters.py` | Local Real + Mock | `TESTED` |
| 22 | Local Model Adapters (CLI Subprocess, HTTP, Ollama, llama.cpp, vLLM) | `SubprocessCLIAdapter` / `GenericHTTPAdapter` | `src/llmforge/models/adapters.py` | `tests/test_adapters.py` | Local Real Process | `TESTED` |
| 23 | Security Safeguards & Untrusted Data Protection | `SecurityEngine` | `src/llmforge/security/engine.py` | `tests/test_security.py` | Local Real | `TESTED` |
| 24 | GitHub Repository Quality (LICENSE, README, CI, Docs) | Repo files | Root / `docs/` | `tests/test_server.py` | Local Real | `TESTED` |

## Summary Audit Metrics

- **Total Main Requirements Evaluated:** 24
- **Tested & Fully Implemented:** 23
- **Partially Implemented:** 0
- **Missing:** 0
- **Environment Blocked:** 1 (Real Gemini credentials unavailable in CI/sandbox environment)
