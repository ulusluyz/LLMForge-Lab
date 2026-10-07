import os
import urllib.parse
from typing import List, Dict, Any

class SecurityEngine:
    """Security Engine providing prompt injection, SSRF, canonical path sandboxing, and zip bomb defenses."""

    @staticmethod
    def sanitize_path(base_dir: str, target_path: str) -> str:
        """Canonical path sandboxing to prevent path traversal attacks."""
        base_abs = os.path.realpath(base_dir)
        target_abs = os.path.realpath(os.path.join(base_abs, target_path) if not os.path.isabs(target_path) else target_path)

        # Block relative or absolute path traversal attempts escaping base_dir
        if not (target_abs == base_abs or target_abs.startswith(base_abs + os.sep)):
            raise ValueError(f"Path traversal blocked: '{target_path}' escapes sandbox '{base_dir}'.")

        if ".." in target_path.split(os.sep):
            raise ValueError(f"Path traversal blocked: '{target_path}' contains parent directory escape.")

        return target_abs

    @staticmethod
    def validate_url(url: str) -> bool:
        """SSRF defense against loopback, private IP ranges, metadata endpoints, and non-HTTP schemes."""
        if not url:
            return False
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ["http", "https"]:
            return False
        hostname = (parsed.hostname or "").lower()
        if hostname in ["localhost", "127.0.0.1", "0.0.0.0", "::1", "169.254.169.254"] or hostname.startswith("192.168.") or hostname.startswith("10.") or hostname.startswith("172.16."):
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

    @staticmethod
    def validate_zip_bomb(decompressed_size: int, file_count: int, max_size_mb: int = 500, max_files: int = 1000) -> bool:
        """Zip bomb decompression safeguard."""
        max_bytes = max_size_mb * 1024 * 1024
        if decompressed_size > max_bytes or file_count > max_files:
            raise ValueError(f"Decompression bomb blocked: size={decompressed_size} bytes, files={file_count}")
        return True
