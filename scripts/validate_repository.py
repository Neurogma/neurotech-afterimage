#!/usr/bin/env python3
"""Offline structural checks for neurotech-afterimage."""

from __future__ import annotations

import re
import sys
from urllib.parse import unquote
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_TOP_LEVEL = (
    "README.md",
    "INDEX.md",
    "CONTRIBUTING.md",
    "LICENSE",
    ".gitignore",
)
CASE_ROOTS = (
    ROOT / "post-mortems" / "startups",
    ROOT / "post-mortems" / "devices-abandoned",
    ROOT / "post-mortems" / "clinical-trials",
)
REQUIRED_METADATA = ("case_id", "title", "format", "outcome")
REQUIRED_SECTIONS = (
    "## Case identity and outcome",
    "## What the public record shows",
    "## What remains unknown",
    "## Questions future teams should ask",
    "## Evidence register",
)
EVIDENCE_LABELS = (
    "Documented fact",
    "Attributed testimony",
    "Reported allegation",
    "Editorial inference",
    "Unknown",
)


def parse_front_matter(text: str) -> dict[str, str]:
    """Parse the repository's intentionally small YAML-like front matter."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}
    metadata: dict[str, str] = {}
    for line in lines[1:end]:
        match = re.match(r"^([a-z_]+):\s*(.*?)\s*$", line)
        if match:
            metadata[match.group(1)] = match.group(2)
    return metadata


def source_ids_in(text: str) -> set[str]:
    return set(re.findall(r"\[(S-[A-Z0-9-]+)\]", text))


def duplicate_source_ids(text: str) -> set[str]:
    """Return source-register identifiers declared more than once."""
    declarations = re.findall(r"^### (S-[A-Z0-9-]+)\s*$", text, re.MULTILINE)
    return {source_id for source_id in declarations if declarations.count(source_id) > 1}


def empty_headings(text: str) -> list[str]:
    """Return Markdown headings with no direct body before the next heading."""
    lines = text.splitlines()
    empty: list[str] = []
    for index, line in enumerate(lines):
        if not re.match(r"^#{1,6}\s+\S", line):
            continue
        title = line.strip()
        body_found = False
        for following in lines[index + 1:]:
            if re.match(r"^#{1,6}\s+\S", following):
                break
            if following.strip():
                body_found = True
                break
        if not body_found:
            empty.append(title)
    return empty


def validate_case_text(
    text: str,
    known_source_ids: set[str],
    *,
    label: str = "case",
) -> list[str]:
    errors: list[str] = []
    metadata = parse_front_matter(text)
    for key in REQUIRED_METADATA:
        if not metadata.get(key):
            errors.append(f"{label}: missing metadata field {key}")
    if "status" in metadata:
        errors.append(f"{label}: status metadata is not used")
    unresolved = re.search(r"\b(?:TODO|TBD|PLACEHOLDER)\b", text, re.IGNORECASE)
    if unresolved:
        errors.append(f"{label}: unresolved editorial placeholder")
    for section in REQUIRED_SECTIONS:
        if section not in text:
            errors.append(f"{label}: missing section {section}")
    for section in empty_headings(text):
        errors.append(f"{label}: empty section heading {section}")
    ids = source_ids_in(text)
    if not ids:
        errors.append(f"{label}: no source identifiers found")
    for source_id in sorted(ids - known_source_ids):
        errors.append(f"{label}: source identifier {source_id} is absent from source register")
    if not any(evidence_label in text for evidence_label in EVIDENCE_LABELS):
        errors.append(f"{label}: no explicit evidence classification found")
    return errors


def validate_repository(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for filename in REQUIRED_TOP_LEVEL:
        if not (root / filename).is_file():
            errors.append(f"missing required top-level file {filename}")
    required_paths = (
        root / "post-mortems" / "post-mortem-template.md",
        root / "post-mortems" / "blameless-language-guide.md",
        root / "docs" / "evidence-and-sourcing.md",
        root / "docs" / "case-screening.md",
        root / "docs" / "editorial-process.md",
        root / "docs" / "validation-record.md",
        root / "sources" / "source-register.md",
        root / "scripts" / "validate_repository.py",
        root / "tests" / "test_repository.py",
    )
    for path in required_paths:
        if not path.is_file():
            errors.append(f"missing required project file {path.relative_to(root)}")
    if errors:
        return errors

    source_text = (root / "sources" / "source-register.md").read_text(encoding="utf-8")
    source_id_declarations = re.findall(r"^### (S-[A-Z0-9-]+)\s*$", source_text, re.MULTILINE)
    known_source_ids = set(source_id_declarations)
    for source_id in sorted(duplicate_source_ids(source_text)):
        errors.append(f"source register contains duplicate identifier {source_id}")
    cases: dict[str, Path] = {}
    case_paths: set[str] = set()
    for case_root in CASE_ROOTS:
        relative_case_root = root / case_root.relative_to(ROOT)
        if not relative_case_root.is_dir():
            errors.append(f"missing case directory {relative_case_root.relative_to(root)}")
            continue
        for path in sorted(relative_case_root.glob("*.md")):
            case_text = path.read_text(encoding="utf-8")
            errors.extend(validate_case_text(
                case_text,
                known_source_ids,
                label=path.relative_to(root).as_posix(),
            ))
            metadata = parse_front_matter(case_text)
            case_id = metadata.get("case_id", "")
            if case_id:
                if case_id in cases:
                    errors.append(f"duplicate case_id {case_id}")
                cases[case_id] = path
            case_paths.add(path.relative_to(root).as_posix())

    index_text = (root / "INDEX.md").read_text(encoding="utf-8")
    index_paths = set(re.findall(r"\]\((post-mortems/[^)]+\.md)\)", index_text))
    if index_paths != case_paths:
        missing = sorted(case_paths - index_paths)
        stale = sorted(index_paths - case_paths)
        if missing:
            errors.append("index missing case links: " + ", ".join(missing))
        if stale:
            errors.append("index contains stale case links: " + ", ".join(stale))

    screening_text = (root / "docs" / "case-screening.md").read_text(encoding="utf-8")
    for candidate in ("Symbionic", "Kernel Flow", "Pikov"):
        if candidate not in screening_text:
            errors.append(f"screening register does not mention {candidate}")

    # Check local Markdown links in repository Markdown files. External links
    # are deliberately not fetched by this offline structural validator.
    link_pattern = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
    for markdown in root.rglob("*.md"):
        text = markdown.read_text(encoding="utf-8")
        for target in link_pattern.findall(text):
            target = target.strip().split(maxsplit=1)[0].strip("<>")
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            local_target = unquote(target.split("#", 1)[0])
            if not local_target:
                continue
            resolved = (markdown.parent / local_target).resolve()
            if not resolved.is_file():
                errors.append(
                    f"{markdown.relative_to(root)}: broken internal link {target}"
                )
    return errors


def main() -> int:
    errors = validate_repository()
    if errors:
        print("Repository validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    total_cases = sum(
        1
        for case_root in CASE_ROOTS
        for path in (ROOT / case_root.relative_to(ROOT)).glob("*.md")
    )
    print(f"Repository validation passed: {len(REQUIRED_TOP_LEVEL)} required top-level files and "
          f"{total_cases} dossier files checked.")
    print("Source IDs, required sections, screening entries and index links are consistent.")
    print("This structural check does not verify factual accuracy or source support.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
