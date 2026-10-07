# Root-Cause Intelligence & Falsification Engine

## Core Architectural Principle: Competing Hypotheses & Falsification

LLMForge Lab enforces a **falsification-first** approach to model diagnosis. Rather than adopting the first plausible explanation, the engine maintains competing hypotheses across the 15 root-cause families and executes discriminating experiments to falsify weaker explanations.

```text
                        MODEL FAILURE OBSERVED
                                  │
                                  ▼
                   EVIDENCE & SIGNAL COLLECTION
                                  │
                                  ▼
                    COMPETING HYPOTHESES RANKING
  ┌───────────────────────────────┼───────────────────────────────┐
  │                               │                               │
Context Truncation        Adapter History Bug            Data Gap
(Prob: 0.45)               (Prob: 0.40)                (Prob: 0.15)
  └───────────────────────────────┼───────────────────────────────┘
                                  │
                                  ▼
                   DISCRIMINATING EXPERIMENT PLANNER
      (Run test directly against runtime vs through LLMForge adapter)
                                  │
                                  ▼
                        FALSIFICATION & UPDATE
        (Adapter test fails; Direct runtime test passes)
                                  │
                                  ▼
                   ROOT CAUSE ISOLATED: ADAPTER BUG
         (Data Requirement Permitted? NO - System bug isolated)
```

## Falsification Rules & Falsified Hypotheses

A hypothesis status transitions through the following lifecycle:
- `PROPOSED`: Initial candidate hypothesis generated from diagnostic signals.
- `SUPPORTED`: Validated by at least one supporting experiment.
- `WEAKENED`: Contradicted by discriminating experiment evidence.
- `FALSIFIED`: Proven false (e.g. direct runtime succeeds while adapter fails).
- `CONFIRMED`: High-confidence surviving hypothesis after competing alternatives are falsified.

## Anti-Data-Bias Gate

Before a `DATA_REQUIREMENT` intervention is permitted, the engine enforces three strict anti-data-bias conditions:
1. Data deficiency hypothesis must have evidence strength >= 0.75.
2. Major technical alternatives (chat templates, adapter history, decoding parameters, tokenizer fertility) must be explicitly evaluated and falsified.
3. No stronger system, runtime, or configuration explanation exists.
