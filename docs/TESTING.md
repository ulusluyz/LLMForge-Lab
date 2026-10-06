# Testing Strategy & Execution Guide

## Test Hierarchy

- **Level A — Unit Tests:** Pure deterministic component tests (adapters, Pydantic schemas, audit hashing).
- **Level B — Integration Tests:** Connected components with mock providers (AdaptiveDiagnosticEngine, PipelineV3, FastAPI TestClient).
- **Level C — Local E2E Tests:** End-to-end execution against local mock/subprocess LLM processes (`tests.fixtures.dummy_model`).
- **Level D — Real External Integration:** Live Gemini API / web research calls (executed when credentials are available).

## Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=llmforge
```
