import uuid
import random
from typing import Dict, Any, List, Optional

class DynamicItemGenerator:
    """Generates dynamic evaluation prompts varying entities, topics, and settings while keeping measurement protocols stable."""

    NAMES_SET_A = ["Selin", "Baran", "Deniz", "Efe", "Zeynep"]
    NAMES_SET_B = ["Ayşe", "Mehmet", "Can", "Gamze", "Bora"]

    LOCATIONS_SET = ["eski bir fabrikada", "teknoloji laboratuvarında", "tarihi bir kütüphanede", "uzay istasyonunda"]
    TOPICS_SET = ["yapay zeka güvenliği", "küresel iklim değişimi", "tarihi mimari restorasyonu", "kuantum bilgisayarlar"]

    @classmethod
    def generate_dynamic_prompt(cls, capability_type: str, turn_index: int, seed: Optional[int] = None) -> Dict[str, Any]:
        if seed is not None:
            random.seed(seed + turn_index)

        names = random.sample(cls.NAMES_SET_A if turn_index % 2 == 0 else cls.NAMES_SET_B, 3)
        location = random.choice(cls.LOCATIONS_SET)
        topic = random.choice(cls.TOPICS_SET)

        if capability_type == "narrative_multi_constraint":
            prompt = (
                f"{names[0]}, {names[1]} ve {names[2]}'nin {location} geçirdiği bir olayı 18-22 satır arasında anlat. "
                f"{names[0]} sabırsız, {names[1]} dikkatli, {names[2]} meraklı olsun. Hikayenin sonunda {topic} konusuna değin. Resmî dil kullanma."
            )
            constraints = {
                "min_lines": 18,
                "max_lines": 22,
                "required_entities": names,
                "required_topic": topic,
                "forbidden_register": "formal"
            }
        else:
            prompt = f"Tur {turn_index}: {topic} konusunda {names[0]} ve {names[1]} arasındaki tartışmayı {location} çerçevesinde anlat."
            constraints = {"required_entities": names[:2]}

        return {
            "item_id": f"dyn_item_{uuid.uuid4().hex[:6]}",
            "prompt": prompt,
            "constraints": constraints,
            "metadata": {"names": names, "location": location, "topic": topic}
        }
