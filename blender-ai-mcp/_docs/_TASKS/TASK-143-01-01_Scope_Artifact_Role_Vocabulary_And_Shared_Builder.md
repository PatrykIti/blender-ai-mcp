# TASK-143-01-01: Scope Artifact, Role Vocabulary, and Shared Builder

**Parent:** [TASK-143-01](./TASK-143-01_Scope_Graph_Contract_And_Read_Only_Surface.md)
**Status:** ✅ Done
**Priority:** 🔴 High

**Completion Summary:** Completed on 2026-04-07. The old private
`_assembled_target_scope(...)` posture was replaced with the shared
`spatial_graph` service, including deterministic anchor selection and bounded
object-role vocabulary for scope artifacts.

## Objective

Define the exact scope-graph artifact and move the current scope derivation
into one reusable shared builder instead of keeping it private to
`reference.py`.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/application/services/`
- `server/adapters/mcp/contracts/scene.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `_docs/LLM_GUIDE_V2.md`

## Acceptance Criteria

- the current `_assembled_target_scope(...)` and anchor-selection logic are
  refactored into one reusable builder outside the MCP wrapper layer
- the builder lands as one explicit application-level module under
  `server/application/services/` rather than remaining only as private helper
  logic spread across MCP adapter code
- the scope artifact explicitly carries:
  - scope kind
  - primary target
  - object set
  - object roles
- the role vocabulary stays bounded and deterministic instead of becoming a
  fuzzy semantic taxonomy
- the same builder can serve stage compare / iterate and later public
  read-only scope queries
- the artifact stays compact enough for frequent guided use and does not create
  a second default checkpoint payload

## Docs To Update

- `_docs/LLM_GUIDE_V2.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/tools/scene/test_scene_contracts.py`

## Changelog Impact

- include in the parent `TASK-143` changelog entry when shipped

## Status / Board Update

- keep board tracking on `TASK-143`
- no `_docs/_TASKS/README.md` change in this planning pass
