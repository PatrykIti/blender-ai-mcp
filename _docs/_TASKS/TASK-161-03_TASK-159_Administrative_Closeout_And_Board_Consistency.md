# TASK-161-03: TASK-159 Administrative Closeout And Board Consistency

**Parent:** [TASK-161](./TASK-161_TASK-159_Closeout_Seam_And_Proof_Lane_Alignment.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Repair the historical task/board/changelog drift left after the first
`TASK-159` closeout so the family no longer reads as open inside its own task
files.

## Repository Touchpoints

- `_docs/_TASKS/TASK-159*.md`
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_CHANGELOG/*.md`

## Implementation Notes

- keep `TASK-159` closed historically
- track the late follow-on explicitly under `TASK-161`
- replace stale open/in-progress wording in `Status / Board Update` sections
  with closed historical wording that points at the follow-on record

## Tests To Add/Update

- none; validate through consistency/audit checks

## Validation Commands

- `git diff --check`
- `rg -n "promote as a board-level open task|keep promoted tracking on parent|keep promoted tracking on the parent board item" _docs/_TASKS/TASK-159*.md`

## Docs To Update

- `_docs/_TASKS/README.md`
- `TASK-159*.md`
- `_docs/_CHANGELOG/README.md`

## Changelog Impact

- include in the parent `TASK-161` changelog entry when shipped

## Acceptance Criteria

- `TASK-159` remains closed, but the late closeout drift is explicitly tracked
  and then closed under `TASK-161`
- the `TASK-159` family no longer carries open-task wording in
  `Status / Board Update`
- board and changelog history stay consistent with the final task states

## Status / Board Update

- completed as a historical child of `TASK-161`
- no separate promoted board row is needed for this slice

## Completion Summary

Completed on 2026-05-05.

- created the explicit `TASK-161` follow-on record for the late `TASK-159`
  closure work
- removed stale open-task wording from the historical `TASK-159` family and
  aligned board/changelog state with the final closed history
