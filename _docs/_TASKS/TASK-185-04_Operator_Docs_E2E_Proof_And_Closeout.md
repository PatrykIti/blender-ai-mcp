# TASK-185-04: Operator Docs, E2E Proof, And Closeout

**Parent:** [TASK-185](./TASK-185_Optional_Generative_3D_Seed_Asset_Intake.md)
**Status:** ⏳ To Do
**Priority:** 🟡 Medium
**Objective:** Close the optional seed-asset intake family with fixture-backed proof, operator documentation, board/changelog updates, and explicit validation accounting.

**Repository Touchpoints:** `_docs/_MCP_SERVER/README.md`, `_docs/_ADDON/README.md`, `_docs/_TASKS/README.md`, `_docs/_CHANGELOG/`, `_docs/_CHANGELOG/README.md`, `tests/e2e/`, `tests/unit/`

## Implementation Notes

- Record which provider or local fixture path was validated.
- Keep live-provider smoke tests optional and gated by explicit env vars.
- Update the board only for promoted status changes; nested leaf closure does
  not require every leaf to become a board row.

## Runtime / Security Contract Notes

- operator docs must include provider-key redaction, artifact trust boundaries,
  timeout/resource limits, and cleanup expectations
- live-provider proof must not be required for default CI

## Tests To Add/Update

- fixture-backed E2E proof
- targeted unit tests for any public contracts or config surfaces
- docs consistency grep for provider/key/redaction wording

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_ADDON/README.md`
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/README.md` when changelog entry is added

## Acceptance Criteria

- task closeout records exact validation commands and skipped live-provider
  lanes
- docs explain default-off provider posture and import side effects
- changelog and board state match the final implementation status

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
