# TASK-159-02: Scene MCP Area Modularization And Surface Slices

**Parent:** [TASK-159](./TASK-159_Modularize_Oversized_Guided_Runtime_And_Scene_Owner_Files.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Split `server/adapters/mcp/areas/scene.py` into bounded internal slices for:

- inspect
- state_reads
- grouped_create_configure
- object_utilities
- spatial_graph
- measure_assert
- view_diagnostics
- viewport_surface

while preserving the current public scene MCP tool names, tool versions, and
router/visibility metadata behavior.

This subtask is intentionally scoped to the named scene concern clusters. The
goal is not to repartition every remaining `scene.py` responsibility in one pass
or invent a second public surface. Macro wrappers plus the request-path/session
bridge remain explicitly in the stable facade during this pass unless a
dedicated follow-on leaf is opened for them.

## Business Problem

`scene.py` currently acts as:

- public FastMCP scene tool registry
- adapter translation layer
- sync/async wrapper host
- task/background bridge entrypoint
- scene context / snapshot / structural-read owner
- scene inspect owner
- scene create / manage / utility owner
- scene spatial-graph owner
- scene measure/assert owner
- viewport/view-diagnostics owner

That is too many concerns for one long-lived file. The risk is not only size.
The risk is that public registration and internal logic stay welded together,
which makes future edits slower and more fragile.

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- likely new sibling helper modules such as:
  - `scene_inspect.py`
  - `scene_state_reads.py`
  - `scene_create_configure.py`
  - `scene_object_utils.py`
  - `scene_spatial_graph.py`
  - `scene_measure_assert.py`
  - `scene_view.py`
  - `scene_viewport.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/providers/core_tools.py`
- `server/adapters/mcp/platform/capability_manifest.py`
- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/router/infrastructure/tools_metadata/scene/`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_scene_context_mega.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/scene/test_macro_place_supported_pair_mcp.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/unit/tools/scene/test_mcp_viewport_output.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_task_mode_tools.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_provider_versions.py`
- `tests/unit/adapters/mcp/test_surface_manifest.py`
- `tests/e2e/tools/scene/test_scene_get_viewport.py`
- `tests/e2e/tools/scene/test_scene_get_viewport_camera.py`
- `tests/e2e/tools/scene/test_scene_measure_tools.py`
- `tests/e2e/tools/scene/test_scene_assert_tools.py`
- `tests/e2e/tools/scene/test_scene_view_diagnostics.py`

## Implementation Notes

- Keep `scene.py` as the public MCP registration/facade file.
- Extract private executors, contract builders, and helper clusters into
  sibling modules grouped by concern.
- Keep tool names, docstrings, and version-policy wiring stable.
- Keep the macro wrappers, registration helpers, and provider/manifest-facing
  imports anchored in the stable facade unless a child leaf explicitly extracts
  only their private helper logic.
- Keep `_hydrate_sync_route_session(...)`,
  `_route_tool_call_report_for_context(...)`,
  `_finalize_macro_execution_result(...)`, and the public `macro_*` wrappers as
  explicit facade seams for this subtask; do not silently fold them into one of
  the named scene slices.
- Keep context/snapshot/structural-read helpers and object-utility wrappers
  explicitly assigned to leaves in this family; do not leave them as an
  undocumented remainder under the grouped create/configure branch.
- Keep grouped `scene_create(...)` / `scene_configure(...)` extraction on its
  own dedicated leaf so the read-heavy state/snapshot branch does not quietly
  absorb write-side mega-tool routing.
- Keep scene spatial-support tools visible through the same metadata and guided
  visibility seams; this task should not silently change discovery behavior.
- Keep `scene_get_viewport(...)`, its output formatting, and its task/background
  bridge explicitly assigned to a dedicated leaf; do not leave viewport capture
  as an implicit remainder under the view-diagnostics branch.
- Preserve the distinction between:
  - public MCP wrapper
  - adapter-side orchestration
  - handler/RPC calls
  - session/guided side effects

## Pseudocode

```python
# scene.py keeps public tool defs
from server.adapters.mcp.areas.scene_inspect import execute_scene_inspect
from server.adapters.mcp.areas.scene_state_reads import execute_scene_context, execute_scene_state_read
from server.adapters.mcp.areas.scene_create_configure import execute_scene_create, execute_scene_configure
from server.adapters.mcp.areas.scene_object_utils import execute_scene_clean_scene, execute_scene_object_utility
from server.adapters.mcp.areas.scene_spatial_graph import execute_scope_graph, execute_relation_graph
from server.adapters.mcp.areas.scene_measure_assert import execute_measure_gap, execute_assert_contact
from server.adapters.mcp.areas.scene_view import execute_view_diagnostics
from server.adapters.mcp.areas.scene_viewport import execute_scene_get_viewport

def scene_measure_gap(ctx, ...):
    return route_tool_call(tool_name="scene_measure_gap", direct_executor=lambda: execute_measure_gap(ctx, ...))
```

## Runtime / Security Contract Notes

- Preserve the current public `scene_*` contract surface exactly unless a
  separate contract task says otherwise.
- Preserve provider registration, manifest exposure, and versioned public-surface
  delivery for the scene family while internal helpers move.
- Preserve guided/session side effects for:
  - stale spatial state
  - spatial-check completion
  - gate-plan refresh
- Do not move long-running or task-aware behavior into files that bypass the
  current background/task bridge.

## Execution Structure

| Order | Branch | Purpose |
|------|--------|---------|
| 1 | [TASK-159-02-01](./TASK-159-02-01_Scene_Public_Facade_Registration_And_Version_Guards.md) | Stabilize public registration, provider/manifest wiring, and version-policy guards before internal extraction |
| 2 | [TASK-159-02-02](./TASK-159-02-02_Scene_Context_Inspect_Snapshot_And_Structural_Read_Slices.md) | Split the read-heavy scene branch into focused context, snapshot/structural-read, and inspect-action leaves instead of one monolithic pass |
| 3 | [TASK-159-02-07](./TASK-159-02-07_Scene_Grouped_Create_And_Configure_Mega_Tool_Split.md) | Separate grouped `scene_create(...)` / `scene_configure(...)` routing and private write-side executors from the read-heavy state branch |
| 4 | [TASK-159-02-03](./TASK-159-02-03_Scene_Spatial_Graph_And_View_Diagnostics_Slices.md) | Separate spatial-graph and view-diagnostics helpers without drifting guided visibility semantics |
| 5 | [TASK-159-02-04](./TASK-159-02-04_Scene_Measure_Assert_And_Guided_Side_Effects.md) | Extract measure/assert helpers and preserve guided stale-state / completion side effects |
| 6 | [TASK-159-02-05](./TASK-159-02-05_Scene_Object_Utility_Manage_And_Guided_Dirtying_Slices.md) | Separate object-utility wrappers such as cleanup, rename, visibility, camera utility, and custom-property operations while preserving guided dirtying/runtime semantics |
| 7 | [TASK-159-02-06](./TASK-159-02-06_Scene_Viewport_Background_Bridge_And_Output_Surface.md) | Separate the public viewport capture/output path so `scene_get_viewport(...)` has an explicit owner for output modes, task-mode background execution, and viewport/camera capture semantics |

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_scene_context_mega.py`
- `tests/unit/tools/scene/test_scene_inspect_mega.py`
- `tests/unit/tools/scene/test_scene_inspect_mesh_topology.py`
- `tests/unit/tools/scene/test_scene_inspect_modifiers.py`
- `tests/unit/tools/scene/test_get_constraints.py`
- `tests/unit/tools/scene/test_scene_create_mega.py`
- `tests/unit/tools/scene/test_scene_configure_mega.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/scene/test_scene_state_assistants.py`
- `tests/unit/tools/scene/test_macro_place_supported_pair_mcp.py`
- `tests/unit/tools/test_mcp_area_main_paths.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/unit/tools/scene/test_mcp_viewport_output.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_scene_guided_scope_requirements.py`
- `tests/unit/adapters/mcp/test_task_mode_tools.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_provider_versions.py`
- `tests/unit/adapters/mcp/test_surface_manifest.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/e2e/tools/scene/test_snapshot_tools.py`
- `tests/e2e/tools/scene/test_scene_inspect_material_slots.py`
- `tests/e2e/tools/scene/test_scene_get_viewport.py`
- `tests/e2e/tools/scene/test_scene_get_viewport_camera.py`
- `tests/e2e/tools/scene/test_scene_configure_roundtrip.py`
- `tests/e2e/tools/scene/test_scene_clean_scene.py`
- `tests/e2e/tools/scene/test_scene_utility_workflow.py`
- `tests/e2e/tools/scene/test_scene_measure_tools.py`
- `tests/e2e/tools/scene/test_scene_assert_tools.py`
- `tests/e2e/tools/scene/test_scene_view_diagnostics.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/scene/test_scene_context_mega.py tests/unit/tools/scene/test_scene_inspect_mega.py tests/unit/tools/scene/test_scene_inspect_mesh_topology.py tests/unit/tools/scene/test_scene_inspect_modifiers.py tests/unit/tools/scene/test_get_constraints.py tests/unit/tools/scene/test_scene_create_mega.py tests/unit/tools/scene/test_scene_configure_mega.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/scene/test_scene_state_assistants.py tests/unit/tools/scene/test_macro_place_supported_pair_mcp.py tests/unit/tools/test_mcp_area_main_paths.py tests/unit/tools/test_handler_rpc_alignment.py tests/unit/tools/scene/test_mcp_viewport_output.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_scene_guided_scope_requirements.py tests/unit/adapters/mcp/test_task_mode_tools.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/adapters/mcp/test_provider_inventory.py tests/unit/adapters/mcp/test_provider_versions.py tests/unit/adapters/mcp/test_surface_manifest.py tests/unit/adapters/mcp/test_structured_contract_delivery.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/tools/scene/test_snapshot_tools.py tests/e2e/tools/scene/test_scene_inspect_material_slots.py tests/e2e/tools/scene/test_scene_get_viewport.py tests/e2e/tools/scene/test_scene_get_viewport_camera.py tests/e2e/tools/scene/test_scene_configure_roundtrip.py tests/e2e/tools/scene/test_scene_clean_scene.py tests/e2e/tools/scene/test_scene_utility_workflow.py tests/e2e/tools/scene/test_scene_measure_tools.py tests/e2e/tools/scene/test_scene_assert_tools.py tests/e2e/tools/scene/test_scene_view_diagnostics.py -q`

## Docs To Update

- `_docs/_MCP_SERVER/README.md` only if module/ownership wording needs maintenance
- `_docs/AVAILABLE_TOOLS_SUMMARY.md` only if descriptions or ownership notes drift during extraction
- `_docs/_TASKS/README.md` only when the task status changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- `scene.py` is reduced to a bounded public registration/facade role for the
  named context/state-read, grouped create/configure, object-utility,
  spatial-graph, measure/assert, view-diagnostics, and viewport-surface slices,
  while any remaining macro/request-path bridge seams stay explicitly retained
  in the facade for this pass
- context/state-read, grouped create/configure, object-utility, spatial-graph,
  measure/assert, view-diagnostics, and viewport-surface concerns have clear
  internal homes
- `scene_get_viewport(...)` no longer survives as an undocumented facade
  remainder and has an explicit owner for output modes plus task/background
  execution semantics
- public scene MCP names, metadata, and guided/discovery behavior remain stable
- provider registration, version-policy delivery, and manifest-backed scene
  discovery remain stable
- targeted unit and e2e lanes prove no public scene-surface regression

## Status / Board Update

- keep promoted tracking on the parent `TASK-159`
- execute this subtask through the leaves below instead of widening it into a
  whole-file repartition of every remaining `scene.py` responsibility
- if macro wrappers or the request-path/session bridge remain the last oversized
  seam after these leaves land, track that as explicit follow-on work instead of
  silently stretching one of the current leaves
- do not promote this slice independently unless it becomes the only remaining
  open branch in the family
