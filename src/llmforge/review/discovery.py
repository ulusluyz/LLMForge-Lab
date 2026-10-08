import os
import json
from collections import Counter
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from llmforge.review.store import HumanFeedbackStore

class TaxonomyCandidate(BaseModel):
    candidate_id: str
    proposed_label_name: str
    category: str = "Discovered Taxonomy Candidate"
    description: str
    frequency: int
    sample_rationales: List[str] = Field(default_factory=list)
    status: str = "PENDING_HUMAN_APPROVAL" # PENDING_HUMAN_APPROVAL, APPROVED, REJECTED

class TaxonomyDiscoveryEngine:
    """Analyzes free-text human reviewer notes to discover recurring missing taxonomy concepts."""

    KEYWORDS_TO_CONCEPTS = {
        "tekrar": ("SEMANTIC_REPETITION", "Metin aynı kavramları farklı kelimelerle yapay şekilde tekrar ediyor."),
        "uzat": ("ARTIFICIAL_INFLATION", "Metin yapay olarak şişirilmiş ve gereksiz uzatılmış."),
        "akıc": ("LOW_FLUENCY", "Metinde düşük akıcılık veya doğal olmayan anlatım kalıpları var."),
        "çeviri": ("TRANSLATION_ARTIFACT", "Metinde belirgin makine çevirisi kokusu veya yabancı dil yapısı var."),
        "reklam": ("COMMERCIAL_SPAM", "Ticari reklam veya promosyon dili baskın.")
    }

    def __init__(self, store: HumanFeedbackStore):
        self.store = store

    def discover_candidates(self, min_frequency: int = 2) -> List[TaxonomyCandidate]:
        records = self.store.load_all_records()
        notes = [r.reviewer_note.lower().strip() for r in records if r.reviewer_note and r.reviewer_note.strip()]

        concept_counts: Counter = Counter()
        concept_samples: Dict[str, List[str]] = {}

        for note in notes:
            for kw, (concept_id, desc) in self.KEYWORDS_TO_CONCEPTS.items():
                if kw in note:
                    concept_counts[concept_id] += 1
                    if concept_id not in concept_samples:
                        concept_samples[concept_id] = []
                    if len(concept_samples[concept_id]) < 3:
                        concept_samples[concept_id].append(note)

        candidates = []
        for concept_id, count in concept_counts.items():
            if count >= min_frequency:
                _, desc = next((v for k, v in self.KEYWORDS_TO_CONCEPTS.items() if v[0] == concept_id), ("", "Discovered Concept"))
                candidates.append(TaxonomyCandidate(
                    candidate_id=f"cand_{concept_id.lower()}",
                    proposed_label_name=concept_id,
                    description=desc,
                    frequency=count,
                    sample_rationales=concept_samples.get(concept_id, []),
                    status="PENDING_HUMAN_APPROVAL"
                ))

        return candidates
