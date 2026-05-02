# TASK-159-02: Scene MCP Area Modularization And Surface Slices

**Parent:** [TASK-159](./TASK-159_Modularize_Oversized_Guided_Runtime_And_Scene_Owner_Files.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Split `server/adapters/mcp/areas/scene.py` into bounded internal slices for:

- inspect
- create/manage
- spatial_graph
- measure_assert
- view

while preserving the current public scene MCP tool names, tool versions, and
router/visibility metadata behavior.

## Business Problem

`scene.py` currently acts as:

- public FastMCP scene tool registry
- adapter translation layer
- sync/async wrapper host
- task/background bridge entrypoint
- scene inspect owner
- scene create/manage owner
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
  - `scene_manage.py`
  - `scene_spatial_graph.py`
  - `scene_measure_assert.py`
  - `scene_view.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/router/infrastructure/tools_metadata/scene/`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/tools/scene/test_scene_measure_tools.py`
- `tests/e2e/tools/scene/test_scene_assert_tools.py`
- `tests/e2e/tools/scene/test_scene_view_diagnostics.py`

## Implementation Notes

- Keep `scene.py` as the public MCP registration/facade file.
- Extract private executors, contract builders, and helper clusters into
  sibling modules grouped by concern.
- Keep tool names, docstrings, and version-policy wiring stable.
- Keep scene spatial-support tools visible through the same metadata and guided
  visibility seams; this task should not silently change discovery behavior.
- Preserve the distinction between:
  - public MCP wrapper
  - adapter-side orchestration
  - handler/RPC calls
  - session/guided side effects

## Pseudocode

```python
# scene.py keeps public tool defs
from server.adapters.mcp.areas.scene_inspect import execute_scene_inspect
from server.adapters.mcp.areas.scene_manage import execute_scene_create, execute_scene_manage
from server.adapters.mcp.areas.scene_spatial_graph import execute_scope_graph, execute_relation_graph
from server.adapters.mcp.areas.scene_measure_assert import execute_measure_gap, execute_assert_contact
from server.adapters.mcp.areas.scene_view import execute_viewport, execute_view_diagnostics

def scene_measure_gap(ctx, ...):
    return route_tool_call(tool_name="scene_measure_gap", direct_executor=lambda: execute_measure_gap(ctx, ...))
```

## Runtime / Security Contract Notes

- Preserve the current public `scene_*` contract surface exactly unless a
  separate contract task says otherwise.
- Preserve guided/session side effects for:
  - stale spatial state
  - spatial-check completion
  - gate-plan refresh
- Do not move long-running or task-aware behavior into files that bypass the
  current background/task bridge.

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/tools/scene/test_scene_measure_tools.py`
- `tests/e2e/tools/scene/test_scene_assert_tools.py`
- `tests/e2e/tools/scene/test_scene_view_diagnostics.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/test_handler_rpc_alignment.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/tools/scene/test_scene_measure_tools.py tests/e2e/tools/scene/test_scene_assert_tools.py tests/e2e/tools/scene/test_scene_view_diagnostics.py -q`

## Docs To Update

- `_docs/_MCP_SERVER/README.md` only if module/ownership wording needs maintenance
- `_docs/AVAILABLE_TOOLS_SUMMARY.md` only if descriptions or ownership notes drift during extraction
- `_docs/_TASKS/README.md` only when the task status changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- `scene.py` is reduced to a bounded public registration/facade role
- inspect, create/manage, spatial-graph, measure/assert, and view concerns have
  clear internal homes
- public scene MCP names, metadata, and guided/discovery behavior remain stable
- targeted unit and e2e lanes prove no public scene-surface regression

## Status / Board Update

- keep promoted tracking on the parent `TASK-159`
- do not promote this slice independently unless it becomes the only remaining
  open branch in the family
