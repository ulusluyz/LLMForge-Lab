from typing import Set

class APIBudgetManager:
    """Configurable budget limit manager preventing API call quota exhaustion or runaway loop costs."""

    def __init__(self, max_calls_per_run: int = 100, max_tokens_per_run: int = 500000):
        self.max_calls = max_calls_per_run
        self.max_tokens = max_tokens_per_run
        self.current_calls = 0
        self.current_tokens = 0

    def consume(self, call_count: int = 1, token_count: int = 0) -> None:
        if self.current_calls + call_count > self.max_calls:
            raise RuntimeError(f"API Call Budget Exhausted: {self.current_calls + call_count} exceeds max {self.max_calls}")
        if self.current_tokens + token_count > self.max_tokens:
            raise RuntimeError(f"API Token Budget Exhausted: {self.current_tokens + token_count} exceeds max {self.max_tokens}")
        self.current_calls += call_count
        self.current_tokens += token_count


class ToolAllowlist:
    """Allowlist-based tool permission manager preventing unauthorized command execution."""

    ALLOWED_ACTIONS: Set[str] = {
        "generate_question",
        "evaluate_response",
        "audit_source",
        "normalize_record",
        "run_preflight",
        "export_corpus"
    }

    @classmethod
    def validate_action(cls, action_name: str) -> bool:
        if action_name not in cls.ALLOWED_ACTIONS:
            raise PermissionError(f"Unauthorized tool action blocked: '{action_name}' is not in Tool Allowlist.")
        return True
