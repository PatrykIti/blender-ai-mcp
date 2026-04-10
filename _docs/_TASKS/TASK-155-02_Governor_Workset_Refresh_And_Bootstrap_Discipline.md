# TASK-155-02: Governor Workset, Refresh, And Bootstrap Discipline

**Parent:** [TASK-155](./TASK-155_Guided_Post_Run_Reliability_Followups.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Harden the guided governor around the runtime loops that still caused wasted
tool calls after TASK-130: over-eager spatial refresh, contradictory
create-then-transform guidance, scope mismatch, checkpoint target drift,
misleading role summaries, and empty-scene bootstrap.

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/discovery/search_surface.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Acceptance Criteria

- empty scenes do not require fake spatial targets before primary workset
  bootstrap
- `modeling_create_primitive(...)` followed by initial bounded
  `modeling_transform_object(...)` is either supported directly or replaced by
  one clear guided action
- spatial-refresh scope mismatches return actionable guidance
- checkpoint tools respect the active workset/scope instead of allowing
  single-object bypasses that hide failing required seams
- `allowed_roles` / `missing_roles` reflect execution policy for
  `checkpoint_iterate` and post-refresh states

## Tests To Add/Update

- Unit:
  - `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
  - `tests/unit/adapters/mcp/test_visibility_policy.py`
  - `tests/unit/adapters/mcp/test_search_surface.py`
  - `tests/unit/adapters/mcp/test_scene_guided_scope_requirements.py`
  - `tests/unit/adapters/mcp/test_context_bridge.py`
- E2E:
  - `tests/e2e/integration/test_guided_surface_contract_parity.py`
  - `tests/e2e/integration/test_guided_streamable_spatial_support.py`
  - `tests/e2e/integration/test_guided_inspect_validate_handoff.py`

## Changelog Impact

- include in the TASK-155 changelog entry when this subtask ships

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-155-02-01](./TASK-155-02-01_Empty_Scene_Bootstrap_Primary_Workset_Path.md) | Add an explicit empty-scene bootstrap path before target-bound spatial checks |
| 2 | [TASK-155-02-02](./TASK-155-02-02_Bounded_Create_And_Initial_Transform_Window.md) | Resolve the documented create-then-transform contradiction |
| 3 | [TASK-155-02-03](./TASK-155-02-03_Scope_Mismatch_Actionable_Guidance.md) | Return actionable active-scope mismatch guidance for spatial refresh tools |
| 4 | [TASK-155-02-04](./TASK-155-02-04_Checkpoint_Target_Scope_Enforcement.md) | Prevent checkpoint target bypasses that ignore active required seams |
| 5 | [TASK-155-02-05](./TASK-155-02-05_Checkpoint_Role_Summary_Consistency.md) | Keep role summaries consistent with allowed execution after checkpoints and refresh |
