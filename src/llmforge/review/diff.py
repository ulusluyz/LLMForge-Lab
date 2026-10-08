import re
import difflib
from typing import List, Dict, Any
from pydantic import BaseModel, Field

class DiffOp(BaseModel):
    op_type: str # REMOVED, ADDED, REPLACED, UNCHANGED
    original_text: str = ""
    edited_text: str = ""
    start_offset: int = 0
    end_offset: int = 0

class DocumentDiffResult(BaseModel):
    original_document: str
    edited_document: str
    diff_ops: List[DiffOp] = Field(default_factory=list)
    removed_spans: List[str] = Field(default_factory=list)
    added_spans: List[str] = Field(default_factory=list)
    detected_structural_patterns: List[str] = Field(default_factory=list)

class SafeCleanupGuard:
    """Classifies corrections as SAFE_DETERMINISTIC vs SEMANTIC_REWRITE."""

    PHONE_REGEX = re.compile(r"(\+?90\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{2}[\s.-]?\d{2}")
    EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    URL_REGEX = re.compile(r"https?://[^\s]+")
    BREADCRUMB_REGEX = re.compile(r"\b\w+\s*>\s*\w+(\s*>\s*\w+)*\b")

    @classmethod
    def classify_correction(cls, original: str, edited: str) -> Dict[str, Any]:
        diff = difflib.ndiff(original.splitlines(), edited.splitlines())
        removed_lines = [line[2:] for line in diff if line.startswith("- ")]

        if not removed_lines and len(edited) < len(original):
            removed_lines = [original.replace(edited, "")]

        is_safe_deterministic = True
        extracted_patterns = []

        for line in removed_lines:
            line_str = line.strip()
            if not line_str:
                continue

            matches_phone = bool(cls.PHONE_REGEX.search(line_str))
            matches_email = bool(cls.EMAIL_REGEX.search(line_str))
            matches_url = bool(cls.URL_REGEX.search(line_str))
            matches_breadcrumb = bool(cls.BREADCRUMB_REGEX.search(line_str))

            if matches_phone:
                extracted_patterns.append("PHONE_NUMBER_PATTERN")
            if matches_email:
                extracted_patterns.append("EMAIL_ADDRESS_PATTERN")
            if matches_url:
                extracted_patterns.append("URL_PATTERN")
            if matches_breadcrumb:
                extracted_patterns.append("BREADCRUMB_NAVIGATION_PATTERN")

            # If removed text does not match known deterministic noise and removes substantial words, classify as semantic rewrite
            if not (matches_phone or matches_email or matches_url or matches_breadcrumb):
                if len(line_str.split()) > 3:
                    is_safe_deterministic = False

        safety_class = "SAFE_DETERMINISTIC" if is_safe_deterministic else "SEMANTIC_REWRITE"
        return {
            "safety_class": safety_class,
            "is_auto_cleanable": is_safe_deterministic,
            "extracted_patterns": list(set(extracted_patterns)),
            "removed_count": len(removed_lines)
        }

class DocumentDiffEngine:
    """Computes document line/span diffs and extracts structural noise patterns."""

    @staticmethod
    def compute_diff(original: str, edited: str) -> DocumentDiffResult:
        s = difflib.SequenceMatcher(None, original, edited)
        diff_ops = []
        removed_spans = []
        added_spans = []

        for tag, i1, i2, j1, j2 in s.get_opcodes():
            orig_sub = original[i1:i2]
            edit_sub = edited[j1:j2]

            if tag == "delete":
                diff_ops.append(DiffOp(op_type="REMOVED", original_text=orig_sub, start_offset=i1, end_offset=i2))
                removed_spans.append(orig_sub)
            elif tag == "insert":
                diff_ops.append(DiffOp(op_type="ADDED", edited_text=edit_sub, start_offset=j1, end_offset=j2))
                added_spans.append(edit_sub)
            elif tag == "replace":
                diff_ops.append(DiffOp(op_type="REPLACED", original_text=orig_sub, edited_text=edit_sub, start_offset=i1, end_offset=i2))
                removed_spans.append(orig_sub)
                added_spans.append(edit_sub)
            elif tag == "equal":
                diff_ops.append(DiffOp(op_type="UNCHANGED", original_text=orig_sub, edited_text=edit_sub, start_offset=i1, end_offset=i2))

        correction_info = SafeCleanupGuard.classify_correction(original, edited)

        return DocumentDiffResult(
            original_document=original,
            edited_document=edited,
            diff_ops=diff_ops,
            removed_spans=removed_spans,
            added_spans=added_spans,
            detected_structural_patterns=correction_info["extracted_patterns"]
        )
