# TASK-127: Guided Utility Public Contract Hardening for `scene_clean_scene`

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** FastMCP Platform / Guided Utility UX
**Estimated Effort:** Medium
**Dependencies:** TASK-086-02, TASK-121-05
**Follow-on After:** [TASK-121-05](./TASK-121-05_Guided_Utility_Capture_Prep_And_Goal_Boundary.md)

## Objective

Harden the `llm-guided` public contract for `scene_clean_scene(...)` so guided
utility flows do not fail when clients or models use the older
`keep_lights` / `keep_cameras` style arguments instead of the current
`keep_lights_and_cameras`.

## Business Problem

The guided utility path already exposes `scene_clean_scene(...)`, but the
runtime still leaks a public-contract mismatch:

- some client/model flows call `scene_clean_scene(keep_lights=True, keep_cameras=True)`
- the current public/runtime contract accepts only
  `keep_lights_and_cameras`
- the result is a validation error during a normal `llm-guided` bootstrap flow
- search/discovery can recover only after one failed attempt, which is bad UX

This is not a Blender/runtime behavior bug. It is a shaped-surface contract and
compatibility problem on a user-facing utility entrypoint.

## Business Outcome

If this task is done correctly:

- guided utility cleanup works on the first try in normal `llm-guided` flows
- the public contract is explicit about the canonical argument shape
- bounded compatibility exists for the old split-flag form if we still want to
  tolerate it
- prompts/docs/tests stop teaching one shape while the runtime accepts another

## Scope

This umbrella covers:

- the public contract and compatibility policy for `scene_clean_scene(...)`
- the `call_tool(...)` / public guided path behavior for old split cleanup args
- prompt/docs/test alignment for the canonical cleanup shape

This umbrella does **not** cover:

- redesigning `scene_clean_scene(...)` behavior itself
- broader scene utility redesign outside this cleanup entrypoint
- reopening the full legacy surface

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/platform/naming_rules.py`
- `server/adapters/mcp/transforms/public_params.py`
- `server/router/infrastructure/tools_metadata/scene/scene_clean_scene.json`
- `tests/unit/adapters/mcp/test_aliasing_transform.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_TASKS/README.md`

## Acceptance Criteria

- the repo defines one explicit canonical public argument shape for
  `scene_clean_scene(...)` on `llm-guided`
- guided utility cleanup does not fail on the first call when a client/model
  uses the old split-flag form, if that compatibility path is intentionally
  supported
- prompt/docs/examples and runtime behavior are aligned
- regression coverage protects the guided utility cleanup path

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md` if public wording changes

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_aliasing_transform.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Changelog Impact

- add a `_docs/_CHANGELOG/*` entry when this umbrella is completed

## Status / Board Update

- add this umbrella to `_docs/_TASKS/README.md` as promoted open work
- close or supersede any follow-on leaves explicitly when the compatibility
  strategy is finalized

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-127-01](./TASK-127-01_Scene_Clean_Scene_Public_Contract_And_Compatibility_Policy.md) | Define the canonical public contract and decide whether/how the old split-flag form is tolerated |
| 2 | [TASK-127-02](./TASK-127-02_Scene_Clean_Scene_Guided_Call_Path_Compatibility.md) | Implement the bounded compatibility/canonicalization path on the guided public surface |
| 3 | [TASK-127-03](./TASK-127-03_Scene_Clean_Scene_Prompts_Docs_And_Regression_Pack.md) | Align prompts/docs and lock the behavior with regression coverage |
