import pytest
from llmforge.characterization.boundary import CapabilityBoundaryDiscoverer

def test_capability_boundary_discovery():
    reasoning_boundary = CapabilityBoundaryDiscoverer.discover_reasoning_boundary(max_steps=8)
    assert reasoning_boundary.max_passing_threshold == 4
    assert reasoning_boundary.degradation_threshold == 5
    assert reasoning_boundary.failing_threshold == 6

    context_boundary = CapabilityBoundaryDiscoverer.discover_context_length_boundary(max_k_tokens=32)
    assert context_boundary.max_passing_threshold == 8192
    assert context_boundary.failing_threshold == 32768
