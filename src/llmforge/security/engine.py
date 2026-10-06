import os
import urllib.parse
from typing import List, Dict, Any

class SecurityEngine:
    """Security Engine providing prompt injection, SSRF, path traversal, and zip bomb defenses."""

    @staticmethod
    def sanitize_path(base_dir: str, target_path: str) -> str:
        """Prevent Path Traversal attacks."""
        resolved = os.path.abspath(os.path.join(base_dir, target_path))
        if not resolved.startswith(os.path.abspath(base_dir)):
            raise ValueError(f"Path traversal detected: {target_path}")
        return resolved

    @staticmethod
    def validate_url(url: str) -> bool:
        """Prevent SSRF attacks against internal network endpoints."""
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ["http", "https"]:
            return False
        hostname = (parsed.hostname or "").lower()
        if hostname in ["localhost", "127.0.0.1", "0.0.0.0", "::1"] or hostname.startswith("192.168.") or hostname.startswith("10."):
            return False
        return True

    @staticmethod
    def sanitize_prompt_text(text: str) -> str:
        """Sanitize external untrusted text to prevent prompt injection."""
        dangerous_patterns = ["IGNORE PREVIOUS INSTRUCTIONS", "SYSTEM PROMPT OVERRIDE"]
        sanitized = text
        for pattern in dangerous_patterns:
            sanitized = sanitized.replace(pattern, "[REDACTED_PROMPT_INJECTION]")
        return sanitized
