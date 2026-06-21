# TASK-184-07: Implementation Docs, Board, And Closeout Proof

**Parent:** [TASK-184](./TASK-184_Vision_3D_Understanding_Audit_Corrections.md)
**Status:** ⏳ To Do
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
- `rg -n "near_dark_far_bright|object-ID.*face|pixel.*face|Cryptomatte.*shipped|TASK-183.*Structural" _docs server tests`
