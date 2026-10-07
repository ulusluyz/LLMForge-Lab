import re
from typing import Any, Dict, List, Union

class SecretRedactor:
    """Centralized Secret Redaction Engine preventing key/secret leakage across logs, audits, and transcripts."""

    DEFAULT_PATTERNS = [
        (re.compile(r"AIzaSy[A-Za-z0-9_-]{33}"), "[REDACTED_GEMINI_KEY]"),
        (re.compile(r"GEMINI_API_KEY\s*=\s*[^\s]+", re.IGNORECASE), "GEMINI_API_KEY=[REDACTED]"),
        (re.compile(r"LLMFORGE_CANARY_DO_NOT_EXPOSE_[A-Za-z0-9_]+"), "[REDACTED_CANARY_SECRET]")
    ]

    @classmethod
    def redact_text(cls, text: str) -> str:
        if not text:
            return ""
        redacted = text
        for pattern, replacement in cls.DEFAULT_PATTERNS:
            redacted = pattern.sub(replacement, redacted)
        return redacted

    @classmethod
    def redact_structure(cls, data: Any) -> Any:
        if isinstance(data, str):
            return cls.redact_text(data)
        elif isinstance(data, dict):
            return {k: cls.redact_structure(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [cls.redact_structure(item) for item in data]
        return data
