import pytest
from llmforge.security.redactor import SecretRedactor

def test_secret_redaction_engine():
    # 1. Redact Gemini key (39 chars total: 'AIzaSy' + 33 chars)
    raw_log = "Error connecting with key AIzaSyA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6789"
    redacted = SecretRedactor.redact_text(raw_log)
    assert "AIzaSy" not in redacted
    assert "[REDACTED_GEMINI_KEY]" in redacted

    # 2. Redact Canary Secret
    transcript = "Transcript containing LLMFORGE_CANARY_DO_NOT_EXPOSE_SECRET_KEY_12345 secret."
    redact_trans = SecretRedactor.redact_text(transcript)
    assert "LLMFORGE_CANARY_DO_NOT_EXPOSE" not in redact_trans
    assert "[REDACTED_CANARY_SECRET]" in redact_trans

    # 3. Redact nested dict structure
    nested = {
        "config": {"env": "GEMINI_API_KEY=secret_12345"},
        "logs": ["Key used: AIzaSy12345678901234567890123456789012345"]
    }
    redacted_struct = SecretRedactor.redact_structure(nested)
    assert redacted_struct["config"]["env"] == "GEMINI_API_KEY=[REDACTED]"
    assert "[REDACTED_GEMINI_KEY]" in redacted_struct["logs"][0]
