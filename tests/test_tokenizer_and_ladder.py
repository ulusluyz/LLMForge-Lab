import pytest
from llmforge.diagnostics.tokenizer_lab import TokenizerLab
from llmforge.diagnostics.ladder import DiagnosticEscalationLadder, EscalationLevel

def test_tokenizer_lab_and_escalation_ladder():
    # 1. Tokenizer Lab
    sample = "Türkiye'nin coğrafi bölgeleri ve doğal güzellikleri incelenmektedir."
    metrics = TokenizerLab.analyze_tokenizer(sample, vocab_size=32000)
    assert 1.5 <= metrics.tokens_per_word <= 2.0
    assert metrics.is_turkish_optimized is True

    # 2. Diagnostic Escalation Ladder
    loc = DiagnosticEscalationLadder.escalate_investigation("Adapter history forwarding failure")
    assert loc.escalation_level == EscalationLevel.LEVEL_2_DIFFERENTIAL
    assert loc.artifact == "src/llmforge/models/adapters.py"
    assert loc.symbol == "SubprocessCLIAdapter.generate"
    assert loc.confidence == 0.95
