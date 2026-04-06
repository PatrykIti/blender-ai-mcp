# TASK-144-02: Visibility Report Contract And Read Surface

**Parent:** [TASK-144](./TASK-144_Camera_Aware_View_Graph_And_Visibility_Diagnostics.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High  
**Depends On:** [TASK-144-01](./TASK-144-01_Projection_View_Space_Contract_And_Runtime_Foundation.md)

## Objective

Build the actual machine-readable visibility-report layer on top of the
projection/view-space foundation.

This subtree should answer:

- which requested targets are visible enough to judge
- which are partial, occluded, or off-frame
- whether the current capture is centered on the relevant scope

while keeping the report separate from truth-space assertions and separate
from the default `reference_compare_*` / `reference_iterate_*` payloads.

## Current Runtime Baseline

The repo already has view-control and deterministic capture orchestration, but
it still lacks an explicit report artifact for visibility/framing state.

Today:

- `reference_compare_current_view(...)` captures and compares, but does not
  return typed visibility facts
- `reference_compare_stage_checkpoint(...)` /
  `reference_iterate_stage_checkpoint(...)` already carry dense compare/truth
  payloads and should not become the default home for a full view report

## Implementation Direction

- derive visibility verdicts from the new projection foundation plus current
  scene/capture semantics
- keep the public surface narrow: one visibility report layer plus the shared
  projection seam, not a broad new atomic family
- preserve support for named-camera and `USER_PERSPECTIVE`
- keep the report explicitly view-space only; it must not masquerade as
  attachment/contact truth

## Repository Touchpoints

- `server/domain/tools/scene.py`
- `server/application/tool_handlers/scene_handler.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/areas/scene.py`
- `server/router/infrastructure/tools_metadata/scene/`
- `blender_addon/application/handlers/scene.py`
- `blender_addon/__init__.py`
- `blender_addon/infrastructure/rpc_server.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_mcp_viewport_output.py`
- `tests/unit/tools/scene/test_isolate_object.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/tools/scene/test_scene_get_viewport.py`
- `tests/e2e/tools/scene/test_scene_get_viewport_camera.py`
- `tests/e2e/tools/scene/test_isolate_object.py`

## Acceptance Criteria

- the repo has one typed visibility-report contract for requested objects or
  scopes
- the report distinguishes visible, partially visible, occluded, and off-frame
  states
- the read surface stays explicit and separate from default reference compare
  payloads
- metadata/docs make the view-space-only boundary explicit

## Docs To Update

- `_docs/LLM_GUIDE_V2.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_mcp_viewport_output.py`
- `tests/unit/tools/scene/test_isolate_object.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/tools/scene/test_scene_get_viewport.py`
- `tests/e2e/tools/scene/test_scene_get_viewport_camera.py`
- `tests/e2e/tools/scene/test_isolate_object.py`

## Changelog Impact

- include in the parent TASK-144 changelog entry when shipped

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-144-02-01](./TASK-144-02-01_Visibility_Verdict_Taxonomy_And_Report_Schema.md) | Define the verdict vocabulary and bounded report schema for view-space visibility diagnostics |
| 2 | [TASK-144-02-02](./TASK-144-02-02_Scene_View_Diagnostics_Surface_RPC_Wiring_And_Metadata.md) | Wire the read surface through scene RPC/MCP registration and router/discovery metadata without reopening bootstrap sprawl |

## Status / Board Update

- this subtask is introduced as part of the TASK-144 execution tree expansion
- `_docs/_TASKS/README.md` is intentionally not updated in this planning pass
  per operator constraint
