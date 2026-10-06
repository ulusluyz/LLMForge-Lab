# Changelog

All notable changes to LLMForge Lab will be documented in this file.

## [0.1.0] - Initial Release

### Added
- Provider-independent Intelligence API system with `GeminiProvider` and `MockProvider`.
- Model Adapters for CLI Subprocesses, Generic HTTP, Ollama, llama.cpp, and vLLM.
- Adaptive Diagnostic Engine with multi-turn hidden test graph execution.
- Root Cause Isolation Engine and Hypothesis / Counter-Hypothesis testing.
- Data Requirement Specification module and Source Research Adapters.
- Corpus Pipeline V3 with streaming, normalization, exact SHA-256 deduplication, durable build checkpoints, and manifests.
- Audit Subsystem with 11 audit modules and SHA-256 hash-chained tamper protection.
- Web GUI Dashboard and Human Review UI at `http://127.0.0.1:8080/review`.
- Full CLI interface (`llmforge serve`, `llmforge run`).
- Complete documentation suite in `docs/` and unit/integration test suite.
