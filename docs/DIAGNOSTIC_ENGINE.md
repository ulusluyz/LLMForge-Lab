# Diagnostic Engine & Hidden Test Graph

The diagnostic engine evaluates local language models through multi-turn dynamic conversation turns rather than isolated benchmarks.

## Hidden Test Graph Structure

The model under test interacts through prompts while LLMForge Lab maintains a hidden dependency graph behind the scenes:

- **Nodes:** Individual test questions (`Q1`, `Q2`, ..., `Q20`).
- **Edges:** Semantic dependencies between turns (`RECALL`, `REFERENCE`, `CONTRADICTION`, `COUNTER_TEST`, `DISTRACTOR`, `COMPOSITION`).

```text
Q1 (Establishes Fact A) ---------------> Q8 (Indirect Delayed Recall of Fact A)
 │                                          │
 └──────> Q5 (Constraint B) ---------------> Q14 (Composition of A + B)
```

## Multi-Objective Signal Extraction

Each conversation turn extracts multiple diagnostic signals simultaneously:
- `correctness`
- `context_retention`
- `clarity`
- `reasoning`
- `instruction_following`
- `Turkish language quality`

## Root Cause Candidate Categories

1. `MODEL_WEIGHTS`
2. `TOKENIZER`
3. `CONTEXT_WINDOW`
4. `INFERENCE_RUNTIME`
5. `PROMPT_TEMPLATE`
6. `DATA_REQUIREMENT`
7. `LLMFORGE_SYSTEM_ERROR`
8. `NO_ACTION`
