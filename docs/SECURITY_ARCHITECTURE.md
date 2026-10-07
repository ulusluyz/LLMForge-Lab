# LLMForge Lab Security Architecture & Threat Model

## Trust Boundaries & Isolation Blueprint

LLMForge Lab enforces strict isolation between untrusted external content and application control logic:

```text
USER / OPERATOR
      │
      ▼
LOCAL WEB UI / CLI (127.0.0.1:8080)
      │
      ▼
TRUSTED APPLICATION CORE
  ├── SECRET REDACTION ENGINE
  ├── API BUDGET MANAGER
  ├── TOOL ALLOWLIST PERMISSION GOVERNANCE
  ├── AUDIT SUBSYSTEM (11 SIGNED AUDITS)
  └── SECURITY ENGINE (CANONICAL PATH SANDBOXING & SSRF DEFENSE)
      │
      ▼
UNTRUSTED EXTERNAL ZONE
  ├── WEB RESEARCH & DOWNLOADS (Sanitized & Checked)
  ├── DATASETS & UNTRUSTED CORPOURA (HTML Escaped)
  ├── LOCAL LLM SUBPROCESS / HTTP RESPONSES
  └── EXTERNAL INTELLIGENCE PROVIDER RESPONSES
```

## Threat Model & Security Controls

| Asset | Threat Vector | Security Control Implemented |
|---|---|---|
| Gemini API Credentials | Log/Trace Exfiltration | `SecretRedactor` auto-scrubs API keys and canary strings across logs, audits, and exception traces. |
| Filesystem & Host Environment | Path Traversal (`../../etc/shadow`) | `SecurityEngine.sanitize_path` enforces realpath canonical sandbox boundaries. |
| Internal Network & Cloud Metadata | SSRF (`127.0.0.1`, `169.254.169.254`) | `SecurityEngine.validate_url` blocks loopback, private IP ranges, metadata endpoints, and non-HTTP schemes. |
| Subprocess Execution | Command Injection | Array-based subprocess execution (`exec_args`) without `shell=True` string expansion. |
| Intelligence API Quota | Unlimited Loop Exhaustion | `APIBudgetManager` enforces maximum API calls and token limits per diagnostic run. |
| Agent Execution Rights | Arbitrary System Execution | `ToolAllowlist` enforces explicit permission allowlists on executable actions. |
| Human Review Web UI | Stored / Reflected XSS | `HTMLSanitizer` escapes all untrusted text fields rendered in the web workspace. |
