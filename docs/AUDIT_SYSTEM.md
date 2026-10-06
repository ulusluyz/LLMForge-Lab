# Audit Subsystem & Tamper Detection

LLMForge Lab treats auditing as a first-class subsystem.

## The 11 Audit Modules

1. **Preflight Audit:** Verifies local process, API key, disk permissions before run starts.
2. **Runtime Audit:** Validates sampling parameters, context limits, and generation flags.
3. **Diagnostic Audit:** Ensures evaluations are backed by evidence and counter-tests.
4. **Source Audit:** Records provenance, URL, license status, and synthetic content risk.
5. **Pipeline Audit:** Validates deduplication ratios, exact Jaccard verification, and split isolation.
6. **Corpus Quality Audit:** Verifies token count distributions, malformed records, and encoding.
7. **Human Review Audit:** Records decision history, timestamps, reviewer notes, and undo logs.
8. **Reproducibility Audit:** Fingerprints Git commit, seeds, config, and system hashes.
9. **Security Audit:** Verifies prompt injection protections, path traversal, and SSRF safeguards.
10. **Regression Audit:** Compares Model V1 vs Model V2 diagnostic improvements and regressions.
11. **Final Audit:** End-to-end audit verifying artifact integrity before marking `READY_FOR_TRAINING`.

## Tamper-Evident SHA-256 Hash Signatures

Every audit JSON output is signed with an internal `hash_signature`:

$$\text{hash\_signature} = \text{SHA256}(\text{JSON\_string}(\text{AuditResult}))$$

Any manual modification of audit log files invalidates the hash signature, ensuring complete tamper detection.
