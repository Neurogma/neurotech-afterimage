"""Unit tests for offline structural case checks."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_repository import duplicate_source_ids, empty_headings, validate_case_text, validate_repository  # noqa: E402


VALID_SAMPLE = """---
case_id: sample-case
title: Sample case
format: documented-case-dossier
outcome: transition
---

## Case identity and outcome
Documented fact: a stated outcome. [S-TEST-01]

## What the public record shows
Chronology: the recorded event occurred.

## What remains unknown
Unknown: later support status.

## Questions future teams should ask
- Who is responsible for continuity?

## Evidence register
| S-TEST-01 | A claim | Public record, 2026 | Scope is limited |
"""


class CaseValidationTests(unittest.TestCase):
    def test_valid_sample_case_passes(self) -> None:
        self.assertEqual(
            validate_case_text(VALID_SAMPLE, {"S-TEST-01"}, label="valid sample"),
            [],
        )

    def test_invalid_sample_case_reports_missing_structure_and_source(self) -> None:
        invalid = """---
case_id: broken
title: Broken
---

## Case identity and outcome
## Evidence register
[S-MISSING-01]
"""
        errors = validate_case_text(invalid, {"S-TEST-01"}, label="invalid sample")
        self.assertTrue(any("missing metadata field format" in error for error in errors))
        self.assertTrue(any("missing section" in error for error in errors))
        self.assertTrue(any("S-MISSING-01" in error for error in errors))

    def test_duplicate_source_register_identifiers_are_detected(self) -> None:
        duplicate_register = "### S-DUP-01\nentry one\n\n### S-DUP-01\nentry two\n"
        self.assertEqual(duplicate_source_ids(duplicate_register), {"S-DUP-01"})

    def test_empty_markdown_sections_are_detected(self) -> None:
        self.assertEqual(empty_headings("## Populated\nBody text.\n\n## Empty\n### Child\nContent."), ["## Empty"])

    def test_case_validation_does_not_require_status_metadata(self) -> None:
        self.assertEqual(validate_case_text(VALID_SAMPLE, {"S-TEST-01"}), [])

    def test_status_metadata_is_rejected(self) -> None:
        with_status = VALID_SAMPLE.replace(
            "format: documented-case-dossier",
            "status: editorial-draft\nformat: documented-case-dossier",
        )
        errors = validate_case_text(with_status, {"S-TEST-01"})
        self.assertTrue(any("status metadata is not used" in error for error in errors))

    def test_real_repository_passes_local_structure_checks(self) -> None:
        self.assertEqual(validate_repository(ROOT), [])


if __name__ == "__main__":
    unittest.main()
