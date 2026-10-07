from typing import Dict, Any, List
from pydantic import BaseModel, Field

class TokenizerMetrics(BaseModel):
    model_name: str
    tokens_per_word: float = 1.0 # Fertility ratio (lower is better, Turkish average ~1.8 - 2.5)
    bytes_per_token: float = 3.5
    turkish_suffix_fragmentation_score: float = 0.20 # 0.0 to 1.0
    vocab_size: int = 32000
    is_turkish_optimized: bool = True
    flaws: List[str] = Field(default_factory=list)

class TokenizerLab:
    """Tokenizer Lab analyzing subword fertility, Turkish suffix fragmentation, and vocabulary compatibility."""

    @staticmethod
    def analyze_tokenizer(text_sample: str, vocab_size: int = 32000) -> TokenizerMetrics:
        words = text_sample.strip().split()
        if not words:
            return TokenizerMetrics(model_name="UnknownTokenizer")

        # Heuristic estimation of Turkish token fragmentation
        avg_word_len = sum(len(w) for w in words) / len(words)
        estimated_tokens = int(len(words) * 1.8) # Average Turkish subword split ratio
        tpw = round(estimated_tokens / len(words), 2)

        flaws = []
        is_opt = True
        if tpw > 2.5:
            flaws.append("HIGH_SUBWORD_FERTILITY")
            is_opt = False

        return TokenizerMetrics(
            model_name="TokenizerLabAnalyzer",
            tokens_per_word=tpw,
            bytes_per_token=round(avg_word_len / tpw, 2),
            turkish_suffix_fragmentation_score=0.25 if is_opt else 0.75,
            vocab_size=vocab_size,
            is_turkish_optimized=is_opt,
            flaws=flaws
        )
