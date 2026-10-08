from pydantic import BaseModel, Field
from typing import List, Optional

class QualityReviewSchema(BaseModel):
    proposed_decision: str = Field(description="ACCEPT, REJECT, HUMAN_REVIEW, or SKIP")
    proposed_labels: List[str] = Field(default_factory=list, description="List of assigned taxonomy label IDs")
    rationale: str = Field(description="Detailed technical rationale for the proposed decision")
    confidence: float = Field(default=0.85, description="Confidence score between 0.0 and 1.0")
    uncertainty: float = Field(default=0.15, description="Uncertainty score between 0.0 and 1.0")
    optional_cleaning_recommendation: Optional[str] = Field(default=None, description="Recommended cleaning/correction actions if cleanable")
