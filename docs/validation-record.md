# Validation record

## Inventory

The repository has 28 dossier files: 9 company/startup dossiers, 8 device dossiers, and 11 clinical-trial files. The clinical-trial set contains 9 individual case dossiers, one synthesis, and one extension. The total is 26 individual cases, one synthesis, and one extension. Templates, screening notes, and guidance documents are not counted as cases.

## Changes recorded

On 2026-11-07, the repository structure and source identifiers were reconciled, the six-tier source hierarchy was added, and the source register's 112 entries were labeled by source type and evidentiary role. The full claim-by-claim factual audit was not completed: none of the 26 individual cases can be described as fully verified against every material claim and source.

On 2026-11-08, the project was renamed neurotech-afterimage. The `status` field was removed from all 28 dossier files and the template; the validator now rejects it if reintroduced. The README was simplified, the license summary was expanded, and generated Python cache files were removed from the deliverable.

## Current checks

Run from the repository root on 2026-11-08.

| Command | Result |
|---|---|
| `python scripts/validate_repository.py` | PASS — required files, dossier structure, source IDs, screening entries, index links, and local Markdown links are consistent. |
| `python -m unittest discover -s tests -v` | PASS — 7 tests. |

These checks validate local structure and consistency. They do not fetch external URLs or confirm that every source supports the claim next to it.

## Limits

- The 26 case dossiers have not received a complete claim-by-claim factual audit.
- No comprehensive external link check was run.
- Some legal and corporate claims depend on secondary databases or organizational announcements rather than directly inspected court or register records.
- Patient-level device operation, component availability, maintenance, software, follow-up, and continuing-care arrangements remain unknown in some cases.
- Trial registry status, posted results, and published interpretation are distinct evidence; this record does not claim a full protocol or statistical-analysis-plan audit.
- Passing the local checks does not establish factual completeness or publication readiness.
