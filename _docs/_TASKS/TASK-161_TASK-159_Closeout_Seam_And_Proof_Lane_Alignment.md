# TASK-161: TASK-159 Closeout Seam And Proof-Lane Alignment

**Status:** ✅ Done
**Priority:** 🔴 High
**Category:** Architecture / Maintainability
**Estimated Effort:** Medium
**Follow-on After:** [TASK-159](./TASK-159_Modularize_Oversized_Guided_Runtime_And_Scene_Owner_Files.md)
**Related:** [TASK-160](./TASK-160_Guided_Client_Feedback_And_Streamable_HTTP_Recovery_UX.md)

## Objective

Close the residual `TASK-159` follow-on drift that remained after the initial
modularization closeout:

- finish the remaining `reference.py` ownership split so the facade no longer
  keeps truth/planner policy by default
- align addon proof lanes and owner docs with the live post-split runtime
- repair the administrative task/board wording drift that still described the
  closed `TASK-159` family as open

## Business Problem

`TASK-159` landed the main oversized-owner modularization correctly enough to
ship, but a later audit still found three classes of residual drift:

- code ownership in `reference.py` still looked more monolithic than the task
  family claimed
- addon structural-read and registration proof lanes lagged behind the live
  mixin/runtime shapes
- `TASK-159*.md` still contained open-task wording inside `Status / Board
  Update`, even though the board and changelog already marked the family done

That combination is risky because it weakens the maintainability value of the
original refactor and makes future audits less trustworthy.

## Business Outcome

After this follow-on:

- `reference.py` remains a stable public facade, but the truth/planner helper
  ownership lives in the dedicated helper modules it was supposed to use
- addon proof lanes describe and validate the live payloads/mixin wiring instead
  of stale pre-split shapes
- `TASK-159` stays closed historically, while the repo also records and closes
  the explicit late follow-on under its own task id

## Non-Goals

- no public MCP tool rename or transport-contract redesign
- no new guided/runtime product behavior beyond what is required to align the
  documented modularization seams and proof lanes
- no reopening of `TASK-159` children under the already closed parent

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-161-01](./TASK-161-01_Reference_Facade_Ownership_And_Test_Seam_Alignment_After_TASK-159.md) | Finish the remaining `reference.py` seam and move direct test dependence to the extracted helper modules |
| 2 | [TASK-161-02](./TASK-161-02_Addon_Proof_Lane_And_Owner_Doc_Alignment_After_TASK-159.md) | Align addon owner docs, structural-read fixtures, and registration/custom-property proof lanes with the live post-split runtime |
| 3 | [TASK-161-03](./TASK-161-03_TASK-159_Administrative_Closeout_And_Board_Consistency.md) | Record and close the late follow-on administratively so `TASK-159` history, board state, and changelog wording no longer drift |

## Repository Touchpoints

| Path / Module | Scope | Why It Is In Scope |
|---------------|-------|--------------------|
| `server/adapters/mcp/areas/reference.py` | MCP facade | Residual planner/truth ownership drift remained here after `TASK-159` |
| `server/adapters/mcp/areas/reference_truth.py` | Truth helper owner | Canonical home for truth-bundle budgeting and related helper logic |
| `server/adapters/mcp/areas/reference_planner.py` | Planner helper owner | Canonical home for ranked correction-candidate assembly and budget trimming |
| `tests/unit/adapters/mcp/test_reference_images.py` | Reference seam proof | Main proof lane that previously still imported private helpers from the facade |
| `blender_addon/application/handlers/scene*.py` | Addon owner map | Live post-split mixin structure that docs/tests must reflect accurately |
| `tests/unit/addon/` | Addon registration proof | Needed to prove the mixin split still maps to the registered RPC surface |
| `_docs/_ADDON/README.md` | Addon owner docs | Explicitly stale after the `SceneHandler` split |
| `_docs/_TASKS/TASK-159*.md` | Historical task family | Needed to remove stale open/in-progress wording from the already closed family |
| `_docs/_TASKS/README.md` | Board sync | Follow-on must be tracked as its own promoted task row, not an open child of `TASK-159` |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|-------|-------------------------|-----|
| `reference.py` seam closeout | targeted unit + full repo unit | helper ownership and staged compare assembly are contract-sensitive |
| addon proof-lane alignment | targeted unit + full repo unit + full E2E runner | stale structural-read and registration proof must match the live Blender-backed path |
| task/admin closeout | `git diff --check` + board/task consistency audit | historical closure wording must match the board/changelog state |

## Docs To Update

- `_docs/_ADDON/README.md`
- `_docs/_TASKS/README.md`
- `TASK-159*.md` files that still carried open-state wording
- `_docs/_CHANGELOG/README.md`

## Changelog Impact

- add one dedicated `_docs/_CHANGELOG/*` entry for this late `TASK-159`
  closeout/alignment follow-on

## Acceptance Criteria

- `reference.py` delegates the remaining truth/planner helper ownership to the
  extracted modules, and the reference unit lane no longer treats the facade as
  the primary private helper seam
- addon docs and unit fixtures reflect the live post-split structural-read and
  registration behavior
- the `TASK-159` family no longer contains open-task wording in
  `Status / Board Update`, and the explicit late follow-on is tracked under
  `TASK-161`
- the full repo unit lane and the full Blender-backed E2E runner are executed
  for the integrated closeout

## Status / Board Update

- promoted and completed as a standalone follow-on after the closed `TASK-159`
  umbrella
- no `TASK-159` child is reopened under the closed parent; the historical
  linkage is preserved through `Follow-on After`

## Completion Summary

Completed on 2026-05-05.

- finished the remaining `reference.py` seam handoff and stopped the main
  reference unit lane from depending on facade-private helper imports
- aligned addon owner docs and proof lanes with the live mixin-based
  `SceneHandler` plus structural-read payload shapes
- repaired the stale `TASK-159` administrative wording and recorded the late
  closeout explicitly under `TASK-161`
