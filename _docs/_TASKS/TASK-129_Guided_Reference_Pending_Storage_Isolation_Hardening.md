# TASK-129: Guided Reference Pending Storage Isolation Hardening

**Status:** ✅ Done
**Priority:** 🔴 High
**Category:** Product Reliability / Guided Session State
**Estimated Effort:** Small
**Dependencies:** TASK-121-02, TASK-124-02
**Follow-on After:** [TASK-124-02](./TASK-124-02_Pending_Reference_Adoption_And_Goal_Lifecycle.md)

**Completion Summary:** Guided blocked-session reference handling now keeps
staged pending references physically and logically separate from already-active
goal references. `reference_images(...)` exposes one combined visible set for
blocked sessions, but staged `attach` persists only the newly staged records in
`pending_reference_images`; blocked-session `remove` / `clear` update the
correct store(s) and clean files without leaving active records pointing at
deleted `stored_path` values.

## Objective

Harden the guided reference lifecycle so active goal-scoped references and
staged pending references cannot alias the same records or file paths when a
session drops back into `needs_input`.

## Business Problem

The original pending-adoption wave made staged references survive blocked
guided sessions, but one edge case remained unsafe:

1. a goal becomes ready and already has active `reference_images`
2. the same goal later returns to `needs_input`
3. `reference_images(action="attach", ...)` stages a new pending reference
4. the adapter seeds pending state from the active list when no pending refs
   exist yet
5. later `reference_images(action="remove"| "clear", ...)` in the blocked path
   can delete files for active refs without removing those active records

That leaves stale active `stored_path` entries behind and can break later
compare / iterate flows that still trust the active record metadata.

## Business Outcome

If this task is done correctly:

- blocked guided sessions can accumulate newly staged references without
  corrupting the already-active reference set
- `list` remains operator-readable even when both active and pending references
  exist
- `remove` / `clear` no longer create stale active records that point at
  deleted temp files
- regression coverage protects the exact ready -> `needs_input` -> stage ->
  remove/clear flow that triggered the review finding

## Scope

This follow-on covers:

- `reference_images(...)` blocked-session bookkeeping for active vs pending
  reference stores
- blocked-session visible-list behavior when both stores exist
- blocked-session file cleanup semantics for `remove` and `clear`
- focused docs/test alignment for the hardened contract

This follow-on does **not** cover:

- changing when pending references are adopted
- changing compare/iterate readiness policy
- introducing persistent reference assets beyond session temp storage

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TASKS/README.md`
- `_docs/_TASKS/TASK-124-02_Pending_Reference_Adoption_And_Goal_Lifecycle.md`

## Acceptance Criteria

- blocked-session staged `attach` writes only new staged refs into
  `pending_reference_images`; active refs are not copied into pending storage
- blocked-session `list` returns one stable visible set across active and
  pending refs without duplicating the same `reference_id`
- blocked-session `remove` can remove a staged ref or an active ref while
  updating the correct store(s)
- blocked-session `clear` removes both visible stores safely when both are in
  play
- the hardened path does not leave active records with deleted `stored_path`
  values after blocked-session `remove` / `clear`

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Changelog Impact

- add one `_docs/_CHANGELOG/*` entry for the guided reference storage-isolation
  hardening

## Status / Board Update

- track this follow-on as a standalone completed board item
- update `TASK-124-02` to point at this completed follow-on explicitly

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
