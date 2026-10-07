import pytest
from llmforge.characterization.reproduction import FailureReproductionRunner

def test_failure_reproduction_runner():
    res = FailureReproductionRunner.run_reproduction_tests(
        "LENGTH_CONSTRAINT_VIOLATION",
        "18-22 satır arasında anlat.",
        "Satır 1..."
    )

    assert res.reproduced is True
    assert res.reproduction_rate == 1.0
    assert len(res.reproduction_evidence) == 3
