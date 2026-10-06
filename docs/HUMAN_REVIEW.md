# Human Review Workspace

The Human Review Web UI is hosted at:

`http://127.0.0.1:8080/review`

## Key UI Features

1. **Automatic Categorization Headlines:** Displays why human review was requested (e.g., "Lisans Belirsiz", "Sentetik İçerik Şüphesi", "Kalite Belirsiz").
2. **Detailed Metadata Cards:** Shows full text preview, source URL, provenance, license status, quality score, and pipeline review signals.
3. **Decision Actions:**
   - `[ KABUL ET ]` (ACCEPT)
   - `[ REDDET ]` (REJECT)
   - `[ SONRA BAK ]` (REVIEW_LATER)
4. **Decision Audit Trail:** Logs reviewer decisions, timestamps, notes, and undo history into `human_review_audit.jsonl`.
5. **Strict Corpus Publishing Rule:** Only records with status `ACCEPT` (automated safe ACCEPT + human review ACCEPT) are admitted into final training corpora.
