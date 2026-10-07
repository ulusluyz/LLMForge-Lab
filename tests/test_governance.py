import pytest
from llmforge.security.governance import APIBudgetManager, ToolAllowlist

def test_governance_controls():
    # 1. API Budget exhaustion
    budget = APIBudgetManager(max_calls_per_run=2)
    budget.consume(1)
    budget.consume(1)
    with pytest.raises(RuntimeError):
        budget.consume(1)

    # 2. Tool Allowlist validation
    assert ToolAllowlist.validate_action("generate_question") is True
    with pytest.raises(PermissionError):
        ToolAllowlist.validate_action("execute_shell_command")
