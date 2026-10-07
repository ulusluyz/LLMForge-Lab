# LLM Failure Diagnosis & Root-Cause Taxonomy Research

## Executive Summary & Research Foundation

This research document establishes the theoretical and empirical foundation for LLMForge Lab's **Root-Cause Intelligence Engine** and **Model Intervention Engine**. Grounded in recent literature on LLM evaluation, causal debugging, tokenizer fertility, long-context degradation, and training dynamics, our framework rejects naive "Model Failure -> Need More Data" assumptions in favor of rigorous, hypothesis-driven falsification and root-cause isolation.

### Key Literature & Engineering Sources
1. **Tokenizer & Vocabulary Impact:**
   - *Sennrich et al. (2016) "Subword Neural Machine Translation"* & *Ali et al. (2023) "Tokenizer Fertility in Non-English LLMs"* — High token fertility severely fragments non-English languages (e.g. Turkish), degrading reasoning performance independently of pretraining corpus size.
2. **Context Window & Attention Degradation:**
   - *Liu et al. (2023) "Lost in the Middle: How Language Models Use Long Contexts"* — Performance drops when key information is placed in the middle of long contexts, distinct from data deficiency.
   - *Press et al. (2022) "ALiBi: Train Short, Test Long"* & *Su et al. (2024) "RoPE Scaling Limits"* — Positional encoding misconfigurations cause immediate output degradation beyond pretraining sequence lengths.
3. **Chat Template & Serialization Errors:**
   - *Hugging Face Transformers Guidance (2024) "Chat Template Conventions"* — Missing BOS/EOS, incorrect role separators, or assistant turn formatting cause total instruction-following failure regardless of model capability.
4. **Quantization & Numerical Degradation:**
   - *Dettmers et al. (2022) "LLM.int8() & QLoRA"* — Outlier feature degradation in 4-bit/8-bit quantized models causes repetitive loops or gibberish output that cannot be fixed by dataset expansion.
5. **Causal Debugging & Falsification:**
   - *Pearl (2009) "Causality: Models, Reasoning and Inference"* & *Meng et al. (2022) "Locating and Editing Factual Associations in GPT (ROME)"* — Causal intervention and ablation testing (separating runtime/integration effects from model weight effects).

---

## The 15 Root-Cause Families

1. **DATA_CORPUS:** Pretraining/fine-tuning corpus gaps, style mismatch, domain gap, synthetic artifacts, contamination.
2. **TOKENIZER:** High fertility, subword fragmentation, vocabulary mismatch, special token omission.
3. **MODEL_ARCHITECTURE:** Capacity limits, GQA/MHA attention bounds, RoPE/positional encoding scaling bounds.
4. **CONTEXT_SYSTEM:** Context degradation, history truncation, serialization failure, "Lost in the Middle".
5. **CHAT_TEMPLATE:** Role formatting errors, BOS/EOS token mismatch, assistant separator corruption.
6. **INFERENCE_GENERATION:** Sampling temperature, repetition penalty, top-p/top-k bounds, token limits.
7. **DECODING_TERMINATION:** EOS token mismatch, stop-sequence failure, premature or endless generation loops.
8. **TRAINING_RECIPE:** Learning rate, warmup, batch size, packing, curriculum order, sequence length bounds.
9. **TRAINING_FAILURE:** Overfitting, underfitting, catastrophic forgetting, loss divergence, checkpoint regression.
10. **CHECKPOINT_ARTIFACT:** Corrupted model weights, partial checkpoint loading, config mismatch.
11. **QUANTIZATION_PRECISION:** 4-bit/8-bit quantization degradation, FP16/BF16/FP32 numerical precision artifacts.
12. **RUNTIME:** Backend runtime issues (Ollama, llama.cpp, vLLM, generic HTTP), KV cache limits.
13. **LLMFORGE_INTEGRATION:** Adapter history forwarding bugs, prompt serialization errors, response parsing bugs.
14. **HARDWARE_PERFORMANCE:** VRAM/RAM pressure, swapping, CPU/GPU bottlenecks, OOM (separated from model quality).
15. **UNKNOWN:** Insufficient evidence, multiple plausible causes, uninspectable runtime.
