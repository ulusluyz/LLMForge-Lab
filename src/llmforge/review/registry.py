import os
import json
import time
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class LabelDefinition(BaseModel):
    label_id: str
    name: str
    category: str
    description: str
    inclusion_criteria: str = ""
    exclusion_criteria: str = ""
    positive_examples: List[str] = Field(default_factory=list)
    negative_examples: List[str] = Field(default_factory=list)
    counter_examples: List[str] = Field(default_factory=list)
    default_action: str = "HUMAN_REVIEW" # ACCEPT, REJECT, HUMAN_REVIEW
    risk_level: str = "MEDIUM" # LOW, MEDIUM, HIGH, CRITICAL
    auto_accept_threshold: float = 0.95
    auto_reject_threshold: float = 0.95
    human_review_threshold: float = 0.70

class LabelRegistry(BaseModel):
    version: str = "1.0.0"
    labels: Dict[str, LabelDefinition] = Field(default_factory=dict)

    def register_label(self, label: LabelDefinition):
        self.labels[label.label_id] = label

    def get_label(self, label_id: str) -> Optional[LabelDefinition]:
        return self.labels.get(label_id)

    @classmethod
    def get_default_registry(cls) -> "LabelRegistry":
        registry = cls(version="1.0.0")

        default_labels = [
            LabelDefinition(
                label_id="ADVERTISEMENT",
                name="Advertisement",
                category="Commercial / Spam",
                description="Commercial promotional sales calls, pricing offers, or affiliate link spam.",
                inclusion_criteria="Direct call to purchase, promotional discount code, or commercial sales pitch.",
                exclusion_criteria="Neutral news reporting about a company or unmonetized product review.",
                positive_examples=["Satın almak için tıklayın! %50 indirim fırsatını kaçırmayın."],
                negative_examples=["Şirket yeni çeyrek finansal sonuçlarını açıkladı."],
                counter_examples=["Ürünü iki hafta inceledik; tarafsız artı ve eksi yönleri şunlardır."],
                default_action="REJECT",
                risk_level="MEDIUM"
            ),
            LabelDefinition(
                label_id="PROPAGANDA_SUSPECTED",
                name="Propaganda Suspected",
                category="Content Risk",
                description="Biased ideological promotion or disinformational advocacy.",
                inclusion_criteria="One-sided rhetorical advocacy, emotional manipulation for political groups.",
                exclusion_criteria="Neutral historical analysis, academic discourse, or court documents.",
                positive_examples=["Doğruları yalnızca tarafımız söyler, diğer tüm kaynaklar haindir."],
                negative_examples=["Tarihçi makalesinde iki tarafın görüşlerini karşılaştırıyor."],
                counter_examples=["Mahkeme tutanağında iddia makamının beyanları şu şekildedir."],
                default_action="HUMAN_REVIEW",
                risk_level="HIGH"
            ),
            LabelDefinition(
                label_id="PII",
                name="Personally Identifiable Information",
                category="Privacy / Secrets",
                description="Private personal information such as phone numbers, national IDs, or private emails.",
                default_action="REJECT",
                risk_level="CRITICAL"
            ),
            LabelDefinition(
                label_id="PROMPT_INJECTION",
                name="Prompt Injection",
                category="Security",
                description="Adversarial text attempting to hijack system prompts or exfiltrate state.",
                default_action="REJECT",
                risk_level="CRITICAL"
            ),
            LabelDefinition(
                label_id="NATURAL_TURKISH",
                name="Natural Turkish / User Language",
                category="Positive Evidence",
                description="High value real-world natural Turkish user dialogue, forum discussion, or informal text. Minor typo tolerance applies.",
                default_action="ACCEPT",
                risk_level="LOW"
            )
        ]

        for lbl in default_labels:
            registry.register_label(lbl)
        return registry
