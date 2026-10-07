# Human Feedback Learning Architecture

## Core Architectural Principle: Provider Independence

LLMForge Lab enforces strict provider independence. Intelligence API providers (e.g. Gemini, OpenAI) act purely as **stateless reasoning engines**. All human evidence, learned policies, calibration parameters, label registries, active learning queues, and decision histories are **persistently owned and stored by LLMForge Lab**.

```text
                           LLMFORGE LAB
                                │
                    Persistent Human Knowledge
                                │
   ┌────────────────────────────┼───────────────────────────┐
   │                            │                           │
Human Feedback Store     Learned Review Policy      Calibration Store
   │                            │                           │
Raw Evidence & Spans     Patterns & Counter-Rules    Uncertainty Stats
   │                            │                           │
Human Corrections        Disagreement History       Active Learning
   └────────────────────────────┼───────────────────────────┘
                                │
                         Context Builder
                                │
                         Reasoning Provider
                                │
            ┌───────────────────┼───────────────────┐
            │                   │                   │
      Gemini Provider    OpenAI Provider     Future Provider
```

## Three-Layer Learning Engine Architecture

1. **Layer A — Raw Human Evidence Store (`HumanFeedbackStore`):**
   - Immutable audit trail recording human decisions, multi-label assignments, passage-level character offset spans `[start, end]`, reviewer notes, and pipeline signals.
2. **Layer B — Learned Review Knowledge (`LearnedReviewPolicy`):**
   - Extracted positive patterns, counter-examples, false positive/negative correction events, label boundaries, and confidence calibration statistics.
3. **Layer C — Current Decision System (`LocalLearnedReviewEngine`):**
   - Evaluates incoming documents against learned knowledge, positive/counter examples, and provider reasoning to assign `AUTO_ACCEPT`, `AUTO_REJECT`, or `HUMAN_REVIEW` decisions.

## Active Learning & Progressive Autonomy Modes

- **Uncertainty & Novelty Selection:** Prioritizes records near decision boundaries or originating from novel domains rather than random sampling.
- **Progressive Autonomy Modes:**
  - `MANUAL`: 100% human review.
  - `SHADOW`: System generates predictions without applying them; predictions are logged against human decisions.
  - `ASSISTED`: High-confidence predictions recommended to reviewer.
  - `AUTONOMOUS`: High-confidence predictions automatically applied; uncertain records routed to human review.
- **Promotion Gates & Golden Validation:** Candidate learned policies must pass validation against a versioned Golden Validation Set with zero regression on critical safety/quality labels before promotion to production.
