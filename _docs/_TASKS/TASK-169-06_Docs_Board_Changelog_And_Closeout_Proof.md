# TASK-169-06: Docs, Board, Changelog, And Closeout Proof

**Parent:** [TASK-169](./TASK-169_Reference_Guided_Quality_Drift_Regression_And_Runtime_Authority.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High
**Objective:** Close the family only after prompt/docs wording, board state, changelog history, and the final validation bundle all agree on the shipped runtime behavior.
**Repository Touchpoints:** `_docs/_TASKS/README.md`, `_docs/_CHANGELOG/README.md`, `_docs/_CHANGELOG/*`, `_docs/_PROMPTS/GUIDED_SESSION_START.md`, `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_VISION/README.md`, `_docs/_TESTS/README.md`
**Acceptance Criteria:**
- docs describe the repaired guided/reference/runtime behavior instead of the pre-fix drift
- board/task/changelog state stays synchronized
- closeout records the actual focused, repo-wide, and Blender-backed proof lanes used by the family

## Implementation Notes

- follow the same closeout discipline used by `TASK-135`, `TASK-166`, and
  `TASK-168`: no docs-only closure before live owner seams and proof lanes
  agree
- keep squirrel as the regression anchor in history, but describe the shipped
  contract generically on public docs

## Docs To Update

- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/README.md`
- one new `_docs/_CHANGELOG/*` entry
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- this task owns the family closeout historical entry

## Status / Board Update

- close `TASK-169` and its nested children in the same branch when the proof is
  real

## Validation Commands

- `git diff --check`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`

## Validation Category

- family closeout governance and repo-standard proof
