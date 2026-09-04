# TASK-131: Ready-Session Pending Reference Visibility Consistency

**Status:** ✅ Done
**Priority:** 🔴 High
**Category:** Product Reliability / Guided Session State
**Estimated Effort:** Small
**Dependencies:** TASK-124-02, TASK-129
**Follow-on After:** [TASK-129](./TASK-129_Guided_Reference_Pending_Storage_Isolation_Hardening.md)

**Completion Summary:** `reference_images(...)` now keeps its ready-session
visible-set semantics consistent when explicit pending refs for another goal are
still present. The merged visible list remains inspectable, and ready-session
`remove` / `clear` now update both the active and pending stores when needed,
so cleanup no longer leaves pending records pointing at deleted `stored_path`
files.

## Objective

Close the remaining contract gap between the merged visible reference list and
the actual state updates performed by ready-session `remove` / `clear`.

## Business Problem

After the earlier blocked-session storage-isolation hardening, one ready-path
edge case remained:

1. the current goal is ready and has active references
2. `pending_reference_images` still contains explicit refs for another goal
3. `reference_images(action="list")` shows one merged visible set
4. `reference_images(action="clear")` deletes files for that merged set
5. the ready-path state write clears only active refs, leaving pending records
   behind with broken `stored_path` metadata

That means the public visible-set contract is internally inconsistent: list
shows pending refs, cleanup deletes their files, but the state path may still
preserve those now-broken pending records.

## Business Outcome

If this task is done correctly:

- ready-session cleanup cannot leave pending records behind with deleted files
- `reference_images(action="remove", reference_id=...)` can remove a visible
  pending ref during a ready session instead of failing on a record the tool
  just listed
- the merged visible-set behavior remains coherent across list/remove/clear
  instead of diverging between blocked and ready sessions

## Scope

This follow-on covers:

- ready-session `reference_images(...)` behavior when merged visibility includes
  explicit pending refs for another goal
- remove/clear consistency across active + pending stores in that ready path
- focused docs and regression updates for the visible-set contract

This follow-on does **not** cover:

- changing adoption rules for goal-matched pending refs
- changing router readiness policy or `pending_reference_count` semantics
- redesigning how mismatched pending refs are surfaced outside
  `reference_images(...)`

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_VISION/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TASKS/README.md`
- `_docs/_TASKS/TASK-129_Guided_Reference_Pending_Storage_Isolation_Hardening.md`

## Acceptance Criteria

- if ready-session `list` exposes explicit pending refs for another goal,
  ready-session `remove` can delete them from pending storage correctly
- if ready-session `clear` deletes files for a merged visible set, it also
  clears any pending records whose files were deleted
- no ready-session cleanup path leaves pending refs behind with missing
  `stored_path` files
- focused regression coverage proves the ready-path edge case

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_VISION/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Changelog Impact

- add one `_docs/_CHANGELOG/*` entry for ready-session visible-set consistency

## Status / Board Update

- track this follow-on as a standalone completed board item
- update `TASK-129` to point at this closed ready-session follow-on

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
