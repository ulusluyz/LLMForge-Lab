# Security Model & Safeguards

LLMForge Lab treats all external web content, user inputs, and local LLM outputs as **untrusted data**.

## Core Security Safeguards

1. **Subprocess Isolation:** Commands executed via `SubprocessCLIAdapter` are sanitized using `shlex.split()` without shell string expansion vulnerabilities.
2. **Path Traversal Protection:** Directory paths for `runs/` and pipeline exports are strictly validated and constrained within project boundaries.
3. **Secret Protection:** API keys (`GEMINI_API_KEY`) are managed exclusively via environment variables or `.env` files. Keys are never logged or committed.
4. **Prompt Injection Safeguards:** Web content ingested during research is sanitized before being passed into intelligence API prompt templates.
5. **Decompression & Zip Bomb Defense:** Size limits are enforced on file downloads and streams prior to processing.
