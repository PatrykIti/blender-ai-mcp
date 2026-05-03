# TASK-159-02-02: Scene Context, Inspect, Snapshot, And Structural Read Slices

**Parent:** [TASK-159-02](./TASK-159-02_Scene_MCP_Area_Modularization_And_Surface_Slices.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Split the read-heavy scene branch into focused leaves for context/selection
reads, snapshot/structural reads, and the `scene_inspect(...)` action matrix so
the branch stays execution-ready under the leaf-size rule without changing
runtime behavior.

This subtask still owns the same read-heavy scene surface, but it should no
longer execute as one monolithic pass:

- `scene_context(...)`
- `scene_inspect(...)`
- `scene_snapshot_state(...)`
- `scene_compare_snapshot(...)`
- `scene_get_hierarchy(...)`
- `scene_get_bounding_box(...)`
- `scene_get_origin_info(...)`

Grouped `scene_create(...)` / `scene_configure(...)` mega tools move under
[TASK-159-02-07](./TASK-159-02-07_Scene_Grouped_Create_And_Configure_Mega_Tool_Split.md).
Standalone object-utility wrappers such as cleanup, rename, visibility, camera
utility, and custom-property operations stay under
[TASK-159-02-05](./TASK-159-02-05_Scene_Object_Utility_Manage_And_Guided_Dirtying_Slices.md).

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- likely new helper modules such as:
  - `server/adapters/mcp/areas/scene_inspect.py`
  - `server/adapters/mcp/areas/scene_state_reads.py`
- `server/adapters/mcp/contracts/scene.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_scene_context_mega.py`
- `tests/unit/tools/scene/test_scene_inspect_mega.py`
- `tests/unit/tools/scene/test_scene_inspect_modifiers.py`
- `tests/unit/tools/scene/test_get_constraints.py`
- `tests/unit/tools/scene/test_scene_state_assistants.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/e2e/tools/scene/test_scene_inspect_material_slots.py`
- `tests/e2e/tools/scene/test_snapshot_tools.py`

## Current Code Anchors

- `scene_context(...)`
- `_scene_get_mode(...)`
- `_scene_list_selection(...)`
- `scene_inspect(...)`
- `scene_snapshot_state(...)`
- `scene_compare_snapshot(...)`
- `scene_get_hierarchy(...)`
- `scene_get_bounding_box(...)`
- `scene_get_origin_info(...)`
- `_scene_inspect_object(...)`
- `_scene_inspect_material_slots(...)`
- `_scene_inspect_modifiers(...)`
- `_scene_get_constraints(...)`
- `_scene_inspect_mesh_topology(...)`
- `_scene_inspect_modifier_data(...)`
- `_scene_inspect_render_settings(...)`
- `_scene_inspect_color_management(...)`
- `_scene_inspect_world(...)`

## Pseudocode

```python
state_read_leaf = {
    "scene_context": ["_scene_get_mode", "_scene_list_selection"],
}
snapshot_structural_leaf = {
    "scene_snapshot_state": ["scene_compare_snapshot", "scene_get_hierarchy", "scene_get_bounding_box", "scene_get_origin_info"],
}
inspect_leaf = {
    "scene_inspect": [
        "object",
        "topology",
        "materials",
        "modifiers",
        "constraints",
        "modifier_data",
        "render",
        "color_management",
        "world",
    ],
}

for public_wrapper in read_heavy_scene_wrappers:
    keep_wrapper_in_scene_py(public_wrapper)
    delegate_to_leaf_executor(public_wrapper)
    preserve_structured_contracts_and_assistant_summary(public_wrapper)
```

## Implementation Notes

- Keep the read-heavy branch split by runtime concern, not alphabetically:
  - context/selection reads
  - snapshot/compare plus structural reads
  - `scene_inspect(...)` action-matrix helpers
- Keep grouped create/configure routing out of scope for this subtask so the
  read-heavy branch stays isolated from write-side mega-tool work.
- Treat the full inspect action matrix as owned scope for this branch:
  object, topology, materials, modifiers, constraints, modifier_data, render,
  color_management, and world.
- Preserve current request validation, assistant-summary plumbing, and
  structured scene contracts across all child leaves.

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-159-02-02-01](./TASK-159-02-02-01_Scene_Context_And_Selection_Read_Slices.md) | Separate `scene_context(...)` plus mode/selection reads into one focused adapter-state leaf |
| 2 | [TASK-159-02-02-02](./TASK-159-02-02-02_Scene_Snapshot_Compare_And_Structural_Read_Slices.md) | Separate snapshot/compare, hierarchy, bbox, and origin helpers into one structural-read leaf |
| 3 | [TASK-159-02-02-03](./TASK-159-02-02-03_Scene_Inspect_Action_Matrix_And_Contract_Slices.md) | Separate the full `scene_inspect(...)` action matrix and its typed contract helpers from the rest of the read-heavy branch |

## Runtime / Security Contract Notes

- keep current request validation, assistant-summary plumbing, and structured
  scene contracts intact
- preserve current read-only semantics and `assistant_summary` behavior for
  context/inspect/snapshot/hierarchy/bbox/origin flows, including topology and
  modifier_data inspect branches
- keep grouped create/configure routing out of scope for this leaf so the
  read-heavy branch remains one focused extraction pass

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_scene_context_mega.py`
- `tests/unit/tools/scene/test_scene_inspect_mega.py`
- `tests/unit/tools/scene/test_scene_inspect_mesh_topology.py`
- `tests/unit/tools/scene/test_scene_inspect_modifiers.py`
- `tests/unit/tools/scene/test_get_constraints.py`
- `tests/unit/tools/scene/test_scene_state_assistants.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/e2e/tools/scene/test_scene_inspect_material_slots.py`
- `tests/e2e/tools/scene/test_snapshot_tools.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/scene/test_scene_context_mega.py tests/unit/tools/scene/test_scene_inspect_mega.py tests/unit/tools/scene/test_scene_inspect_mesh_topology.py tests/unit/tools/scene/test_scene_inspect_modifiers.py tests/unit/tools/scene/test_get_constraints.py tests/unit/tools/scene/test_scene_state_assistants.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/test_handler_rpc_alignment.py tests/unit/adapters/mcp/test_structured_contract_delivery.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/tools/scene/test_scene_inspect_material_slots.py tests/e2e/tools/scene/test_snapshot_tools.py -q`

## Docs To Update

- inherit parent docs closeout unless inspect/create ownership wording changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- this branch is decomposed into focused child leaves instead of one oversized
  read-heavy implementation pass
- current scene contracts, assistant-summary hooks, and read-heavy wrappers
  remain stable across context, snapshot/structural, and inspect-action leaves
- unit plus focused inspect and snapshot E2E lanes still prove the same
  context/inspect/snapshot behavior across object, materials, modifiers,
  constraints, topology, modifier_data, render/color_management/world, and
  structural-read branches

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
- execute this branch through the focused leaves below instead of stretching it
  into one read-heavy implementation pass
- keep grouped create/configure work on `TASK-159-02-07` instead of widening
  this subtask back into write-side routing work
