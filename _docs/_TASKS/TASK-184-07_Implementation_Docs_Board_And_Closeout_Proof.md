# TASK-184-07: Implementation Docs, Board, And Closeout Proof

**Parent:** [TASK-184](./TASK-184_Vision_3D_Understanding_Audit_Corrections.md)
**Status:** ✅ Done
**Completion Date:** 2026-06-22
**Completion Summary:** Updated TASK-184 hierarchy status, board rows/counts, historical notes for TASK-179/TASK-180/TASK-183, Vision/MCP/tool/test docs, and changelog entry/index. Final validation records focused unit lanes, lint/type checks, full unit validation, and the Blender E2E runner outcome.
**Priority:** 🟡 Medium
**Objective:** Keep task governance, historical docs, changelog entries, and validation proof synchronized while `TASK-184` implementation slices land.

**Repository Touchpoints:** `_docs/_TASKS/README.md`, `_docs/_TASKS/TASK-179_Blender_Depth_Normal_And_Object_ID_Auxiliary_Passes.md`, `_docs/_TASKS/TASK-180_Set_Of_Mark_Object_Bound_Visual_Marks.md`, `_docs/_TASKS/TASK-183_Capability_Enriched_Vision_Schema_And_Deterministic_Cross_Check.md`, `_docs/_VISION/README.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_CHANGELOG/`, `_docs/_CHANGELOG/README.md`

## Implementation Notes

- Keep `TASK-179`, `TASK-180`, and `TASK-183` closed. Add only historical
  follow-on notes when implementation slices land.
- Keep `_docs/_TASKS/README.md` board rows aligned with actual task statuses.
- Add changelog entries when implementation changes ship, not merely for
  unimplemented planning stubs.
- Run consistency grep for known audit-drift phrases before closeout.

## Runtime / Security Contract Notes

- docs must preserve the authority split: FastMCP/platform discovery,
  deterministic router policy, optional VLM/perception advisory evidence, and
  Blender inspection/assertion truth
- public surface docs must state visibility, read-only/mutating behavior,
  side-effect boundaries, and default-off settings for any changed tool surface

## Tests To Add/Update

- public-surface docs tests when public contracts change
- targeted consistency grep for audit-drift strings
- changelog/index validation if a new changelog entry is added

## Docs To Update

- `_docs/_TASKS/README.md`
- completed task files that need follow-on notes
- `_docs/_CHANGELOG/README.md` when changelog entries are added

## Acceptance Criteria

- no open direct child remains under a closed parent
- board counts and promoted rows match the task files
- closeout records unit/E2E/pre-commit validation that actually ran

## Validation Commands

- `git diff --check`
- run the TASK-184 forbidden-phrase guard over `_docs`, `server`, and `tests`

## Validation Run

- `git diff --check` -> passed before closeout edits; final rerun recorded in the parent task.
- TASK-184 forbidden-phrase guard -> no matches.
- `PYTHONPATH=. poetry run pytest ./tests/unit` -> 3643 passed.
- `poetry run python scripts/run_e2e_tests.py` -> 493 passed, 5 skipped, 2 failed before the final two E2E fixes.
- `PYTEST_ADDOPTS="-k 'openrouter_google_family_compare_profile_reaches_final_contract or capture_stage_images_emits_set_of_mark_overlay_for_object_set'" poetry run python scripts/run_e2e_tests.py --skip-build` -> 2 passed, 498 deselected after the final E2E fixes.
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure` -> passed after one `ruff format` auto-format rerun.
