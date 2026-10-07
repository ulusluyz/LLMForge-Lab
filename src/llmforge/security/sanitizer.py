import html

class HTMLSanitizer:
    """HTML Sanitizer preventing Stored/Reflected XSS attacks in Human Review Web UI."""

    @staticmethod
    def escape_untrusted_text(text: str) -> str:
        if not text:
            return ""
        # Escape HTML special characters
        escaped = html.escape(text)
        return escaped
