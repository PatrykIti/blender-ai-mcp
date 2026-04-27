# TASK-144-02-02: Scene View Diagnostics Surface, RPC Wiring, And Metadata

**Parent:** [TASK-144-02](./TASK-144-02_Visibility_Report_Contract_And_Read_Surface.md)
**Status:** ✅ Done
**Priority:** 🔴 High
**Depends On:** [TASK-144-01-02](./TASK-144-01-02_Blender_View_Projection_Runtime_And_Frame_Coverage.md), [TASK-144-02-01](./TASK-144-02-01_Visibility_Verdict_Taxonomy_And_Report_Schema.md)

**Completion Summary:** Completed on 2026-04-07. Wired the new view
diagnostics surface through the normal scene stack: domain/application APIs,
scene RPC registration, public MCP exposure, router metadata, dispatcher
mapping, provider inventory, and structured delivery regressions now all
cover `scene_view_diagnostics(...)`.

## Objective

Expose the new view diagnostics through the scene read surface and wire the
runtime through the existing server/addon boundary.

This leaf owns:

- scene RPC registration
- MCP wrapper exposure
- router/discovery metadata
- public tool inventory alignment

It does not own guided adoption policy; that belongs to TASK-144-03.

## Implementation Direction

- keep the public seam narrow and explicit
- reuse the existing `scene` provider rather than inventing a parallel area
- ensure the new read surface can be discovered and documented without
  automatically becoming bootstrap-visible on `llm-guided`
- keep the wiring read-only and aligned with current scene utility/inspection
  conventions

## Repository Touchpoints

- `server/domain/tools/scene.py`
- `server/application/tool_handlers/scene_handler.py`
- `server/adapters/mcp/areas/scene.py`
- `server/router/infrastructure/tools_metadata/scene/`
- `blender_addon/__init__.py`
- `blender_addon/infrastructure/rpc_server.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_mcp_viewport_output.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Acceptance Criteria

- the new view diagnostics are callable through the scene MCP/RPC surface
- router/discovery metadata can describe the diagnostics without implying
  truth-space authority
- provider inventory, public inventory, and surface docs stay aligned with the
  chosen narrow scene surface
- the work does not enlarge the default `llm-guided` bootstrap surface by
  itself

## Docs To Update

- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_mcp_viewport_output.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Changelog Impact

- include in the parent TASK-144 changelog entry when shipped

## Status / Board Update

- closed on 2026-04-07 with the TASK-144 visibility wave
- tracked as completed through the closed parent/subtask state
