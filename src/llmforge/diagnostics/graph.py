from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class DependencyType(str, Enum):
    RECALL = "RECALL"
    REFERENCE = "REFERENCE"
    CONSTRAINT = "CONSTRAINT"
    DERIVATION = "DERIVATION"
    CONTRADICTION = "CONTRADICTION"
    PARAPHRASE = "PARAPHRASE"
    DISTRACTOR = "DISTRACTOR"
    COMPOSITION = "COMPOSITION"
    COUNTER_TEST = "COUNTER_TEST"

class TestEdge(BaseModel):
    source_id: str
    target_id: str
    edge_type: DependencyType
    description: str = ""

class QuestionNode(BaseModel):
    id: str
    turn_index: int
    prompt: str
    target_capabilities: List[str] = Field(default_factory=list)
    system_instruction: Optional[str] = None
    expected_signals: List[str] = Field(default_factory=list)
    is_counter_test: bool = False
    parent_hypothesis_id: Optional[str] = None

class HiddenTestGraph(BaseModel):
    nodes: Dict[str, QuestionNode] = Field(default_factory=dict)
    edges: List[TestEdge] = Field(default_factory=list)

    def add_node(self, node: QuestionNode) -> None:
        self.nodes[node.id] = node

    def add_edge(self, source_id: str, target_id: str, edge_type: DependencyType, description: str = "") -> None:
        self.edges.append(TestEdge(
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            description=description
        ))
