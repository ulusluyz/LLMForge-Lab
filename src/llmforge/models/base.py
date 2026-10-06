from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class CapabilityStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    NOT_TESTED = "NOT_TESTED"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"
    AVAILABLE = "AVAILABLE"

class ModelInfo(BaseModel):
    model_name: str = "UNKNOWN"
    model_type: str = "UNKNOWN"
    context_length: Any = CapabilityStatus.UNKNOWN.value
    tokenizer_info: Any = CapabilityStatus.UNKNOWN.value
    chat_template: Any = CapabilityStatus.UNKNOWN.value
    generation_parameters: Dict[str, Any] = Field(default_factory=dict)
    runtime_info: Dict[str, Any] = Field(default_factory=dict)

class GenerationResponse(BaseModel):
    text: str
    raw_response: Dict[str, Any] = Field(default_factory=dict)
    execution_time_seconds: float = 0.0
    status: str = "SUCCESS"
    error_message: Optional[str] = None
