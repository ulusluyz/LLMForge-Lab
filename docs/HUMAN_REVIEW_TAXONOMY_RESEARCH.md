# Human Review Taxonomy Research & Corpus Quality Guidance

## Executive Summary & Research Foundation

This research document grounds LLMForge Lab's Human Review Taxonomy in established dataset curation, human annotation, and responsible AI literature. Rather than relying on a single commercial moderation list or ad-hoc keywords, our taxonomy synthesizes principles from:

1. **Responsible AI & Dataset Curation Literature:**
   - *Gebru et al. (2021) "Datasheets for Datasets"* — Provenance, collection contexts, and governance metadata.
   - *Bender et al. (2021) "On the Dangers of Stochastic Parrots"* — Environmental, toxicity, and documentation risks in large uncurated web corpora.
2. **Quality & Filtering Benchmarks:**
   - *RefinedWeb (Penedo et al., 2023)* — Multistage quality filtering, exact/near deduplication, and boilerplate removal.
   - *FineWeb (Hugging Face, 2024)* — Synthetic data filtering, C4 quality heuristics, line/word-level repetition detection.
   - *Dolma (Soldaini et al., 2024)* — Open web curation pipeline, PII detection, and license taxonomy.
3. **Human Annotation & Active Learning Systems:**
   - *Settles (2009) "Active Learning Literature Survey"* — Uncertainty sampling, margin sampling, and diversity query strategies.
   - *Klie et al. (2022) "Annotation Systems & Quality Control"* — Inter-annotator agreement, adjudication workflows, and passage-level span annotation.

---

## Taxonomy Architecture & Design Principles

### Core Principles
1. **Multi-Label Support:** A single document or text passage can carry multiple labels across orthogonal categories (e.g., `ADVERTISEMENT` + `SEO_SPAM`).
2. **Passage-Level Span Granularity:** Annotations record character offsets `[start, end]` so training signals isolate specific offending spans rather than penalizing entire documents.
3. **No Naive Keyword Blacklists:** Contextual labels (such as `PROPAGANDA_SUSPECTED` or `ADVERTISEMENT`) evaluate discourse intent, positive evidence, counter-evidence, and rhetorical context rather than simple word matches.

---

## Complete Category Taxonomy & Label Registry

### 1. Decision Status
- `ACCEPT`: Approved for final training corpus.
- `REJECT`: Excluded from corpus.
- `HUMAN_REVIEW`: Pending human verification.
- `REVIEW_LATER`: Deferred by reviewer.
- `QUARANTINE`: Suspended pending security/legal adjudication.

### 2. Quality & Structural Defects
- `BROKEN_TEXT`: Text with severe structural corruption or missing content.
- `OCR_GARBAGE`: Garbled text resulting from optical character recognition failure.
- `ENCODING_ERROR`: Malformed UTF-8, mojibake, or unprintable character sequences.
- `LOW_INFORMATION`: Extremely short or low-density text lacking training value.
- `BOILERPLATE`: Repetitive header, footer, navigation, or legal notice text.
- `EXCESSIVE_REPETITION`: Repetitive N-grams, line looping, or word flooding.
- `KEYWORD_SPAM`: Unnatural keyword stuffing designed for search rank manipulation.
- `MALFORMED_CONTENT`: Unparsed JSON, raw HTML tags, or unformatted code snippets.

### 3. Duplicate & Redundancy
- `EXACT_DUPLICATE`: Identical SHA-256 hash match with an existing document.
- `NEAR_DUPLICATE`: High Jaccard/MinHash similarity match (>= 0.80).
- `SEMANTIC_DUPLICATE`: Paraphrased content conveying identical semantic information.
- `TEMPLATE_DUPLICATE`: Documents generated from fixed boilerplate templates with minor variable substitutions.

### 4. Source & Provenance
- `UNKNOWN_SOURCE`: Missing or unidentifiable source origin.
- `LOW_TRUST_SOURCE`: Originating from untrusted, unverified, or scraper sources.
- `MISSING_PROVENANCE`: Missing chain-of-custody or acquisition metadata.
- `SOURCE_CONFLICT`: Conflicting metadata between source inventory and document payload.
- `SOURCE_QUALITY_CONCERN`: Domain or source with high historical rejection rates.

### 5. Licensing & Usage Rights
- `LICENSE_UNKNOWN`: License status is unspecified or missing.
- `LICENSE_RESTRICTED`: Commercial or training use explicitly restricted by terms.
- `LICENSE_CONFLICT`: Incompatible license declarations across data sources.
- `USAGE_RIGHTS_UNCLEAR`: Legal status for AI training is ambiguous.

### 6. Language & Fluency
- `WRONG_LANGUAGE`: Non-target language content (e.g., English text in Turkish corpus).
- `MIXED_LANGUAGE`: Unintentional language switching within a single document.
- `POOR_TURKISH`: Unnatural grammar, severe misspellings, or awkward syntax.
- `MACHINE_TRANSLATION_SUSPECTED`: Low-quality automated translation artifacts.
- `UNNATURAL_LANGUAGE`: Word salad or dysfluent generation.

### 7. Synthetic & AI-Generated Content
- `AI_GENERATED_SUSPECTED`: Unannotated AI generator output.
- `SYNTHETIC_SPAM`: Mass-generated low-quality synthetic QA pairs or dialogue loops.
- `MASS_GENERATED_CONTENT`: Automated template-filled content.

### 8. Privacy & Secrets
- `PII`: Personally Identifiable Information (names, phone numbers, addresses, emails).
- `SENSITIVE_PII`: Government IDs, financial numbers, medical records, or passwords.
- `CREDENTIAL`: API keys, tokens, or private RSA keys.
- `SECRET`: Confidential internal documents or proprietary credentials.
- `PRIVATE_DATA`: Private personal conversations or unconsented personal records.

### 9. Security & Poisoning
- `PROMPT_INJECTION`: Instructions attempting to override system behavior or exfiltrate state.
- `MALICIOUS_INSTRUCTION`: Code or instructions promoting malware creation or exploits.
- `DATA_POISONING_SUSPECTED`: Adversarial text designed to degrade model alignment or accuracy.

### 10. Commercial & Spam
- `ADVERTISEMENT`: Direct commercial purchase calls, promotional pricing, or sales pitches.
- `PRODUCT_PROMOTION`: Biased product endorsements or affiliate link spam.
- `AFFILIATE_CONTENT`: Monetized affiliate referral links.
- `SEO_SPAM`: Search engine optimization spam.
- `CLICKBAIT`: Sensationalized headline content lacking body substance.
- `COMMERCIAL_SPAM`: Unsolicited commercial message flooding.

### 11. Corpus Suitability
- `OFF_TOPIC`: Content outside domain scope.
- `DOMAIN_MISMATCH`: Technical jargon or specialized content assigned to wrong domain.
- `STYLE_MISMATCH`: Inappropriate register or style for target corpus.
- `DIAGNOSTIC_TARGET_MISMATCH`: Content failing to address targeted diagnostic root cause.
- `LOW_TRAINING_VALUE`: Content providing no meaningful linguistic or reasoning signal.

### 12. Benchmark Contamination
- `BENCHMARK_LEAKAGE`: Verbatim test prompts from evaluation benchmarks (e.g., MMLU, GSM8K, AGIEval).
- `TEST_CONTAMINATION`: Near-duplicate variations of standard evaluation benchmark questions.
- `KNOWN_EVAL_CONTENT`: Evaluation dataset content found in training stream.
