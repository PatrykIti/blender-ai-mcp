# TASK-144-01-01: View Query Selector And Projection Contract

**Parent:** [TASK-144-01](./TASK-144-01_Projection_View_Space_Contract_And_Runtime_Foundation.md)
**Status:** ✅ Done
**Priority:** 🔴 High
**Depends On:** [TASK-121-03-03](./TASK-121-03-03_Camera_Faithful_Viewport_Capture_Semantics.md), [TASK-121-03-04](./TASK-121-03-04_User_View_Manipulation_For_Viewport_Capture.md), [TASK-121-03-05](./TASK-121-03-05_Render_Visibility_Consistency_For_Viewport_Capture.md)

**Completion Summary:** Completed on 2026-04-07. Added the typed request and
response vocabulary for view-space diagnostics, including requested/resolved
view provenance, compact projected extent/center evidence, frame-coverage
facts, and explicit unavailable/off-frame/behind-view cases.

## Objective

Define one compact typed contract for querying view-space state from an
existing Blender camera or viewport source.

The contract must make it explicit:

- what view source was requested
- what view source was actually resolved
- what projected screen-space facts are returned
- which facts are unavailable because the active viewport/camera path cannot
  support the query

## Implementation Direction

- keep this leaf focused on request/response vocabulary and method signatures
- separate raw projection/frame facts from later visibility verdicts
- encode provenance such as named camera vs `USER_PERSPECTIVE` directly in the
  payload so downstream code does not need to infer it from prompt text
- keep the payload bounded enough to be reusable by guided flows without
  turning into a full view graph

## Repository Touchpoints

- `server/domain/tools/scene.py`
- `server/application/tool_handlers/scene_handler.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/areas/scene.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`

## Acceptance Criteria

- one typed contract exists for a view-space query over a requested object or
  scope
- the contract distinguishes named-camera and `USER_PERSPECTIVE` selectors
- the response includes projected center, coarse 2D extent, frame-coverage
  facts, and availability/provenance status
- the contract does not yet claim visibility, occlusion, or 3D truth verdicts

## Docs To Update

- `_docs/LLM_GUIDE_V2.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`

## Changelog Impact

- include in the parent TASK-144 changelog entry when shipped

## Status / Board Update

- closed on 2026-04-07 with the TASK-144 foundation wave
- tracked as completed through the closed parent/subtask state
