from abc import ABC, abstractmethod
from typing import List, Dict, Any
from llmforge.research.schemas import DataRequirementSpec, SourceAuditRecord

class SourceResearchAdapter(ABC):
    @abstractmethod
    async def discover_sources(self, spec: DataRequirementSpec) -> List[SourceAuditRecord]:
        pass

class MockResearchAdapter(SourceResearchAdapter):
    async def discover_sources(self, spec: DataRequirementSpec) -> List[SourceAuditRecord]:
        return [
            SourceAuditRecord(
                source_id="src_001",
                source_url="https://example.com/datasets/turkish_dialogues.jsonl",
                source_type="web_dataset",
                provenance="Example Dataset Repo",
                license_status="CC-BY-4.0",
                language="tr",
                quality_signal_score=0.88,
                diagnostic_relevance_score=0.92,
                duplicate_risk=0.05,
                synthetic_risk=0.10,
                decision="ACCEPT",
                decision_reason="High quality Turkish dialogue dataset matching diagnostic requirement."
            ),
            SourceAuditRecord(
                source_id="src_002",
                source_url="https://example.com/datasets/unclear_license.jsonl",
                source_type="web_dataset",
                provenance="Public Crawl",
                license_status="UNKNOWN",
                language="tr",
                quality_signal_score=0.65,
                diagnostic_relevance_score=0.70,
                duplicate_risk=0.20,
                synthetic_risk=0.50,
                decision="HUMAN_REVIEW",
                decision_reason="License is UNKNOWN and high synthetic risk detected."
            )
        ]
