# TASK-159-02-07: Scene Grouped Create And Configure Mega Tool Split

**Parent:** [TASK-159-02](./TASK-159-02_Scene_MCP_Area_Modularization_And_Surface_Slices.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Extract grouped `scene_create(...)` and `scene_configure(...)` routing plus
their private write-side executors from `scene.py` so the read-heavy
context/inspect/snapshot branch does not remain coupled to grouped scene writes.

This leaf owns the public mega-tool wrappers and their action dispatch for:

- `scene_create(...)`
- `scene_configure(...)`

Standalone object-utility wrappers such as cleanup, rename, visibility, camera
utility, and custom-property operations stay under
[TASK-159-02-05](./TASK-159-02-05_Scene_Object_Utility_Manage_And_Guided_Dirtying_Slices.md).

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- likely new helper module such as
  `server/adapters/mcp/areas/scene_create_configure.py`
- `server/adapters/mcp/contracts/scene.py`
- `tests/unit/tools/scene/test_scene_create_mega.py`
- `tests/unit/tools/scene/test_scene_configure_mega.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/e2e/tools/scene/test_scene_configure_roundtrip.py`

## Current Code Anchors

- `scene_create(...)`
- `_scene_create_light(...)`
- `_scene_create_camera(...)`
- `_scene_create_empty(...)`
- `scene_configure(...)`
- `_scene_configure_render_settings(...)`
- `_scene_configure_color_management(...)`
- `_scene_configure_world(...)`

## Planned Code Shape

```python
from .scene_create_configure import (
    execute_scene_create,
    execute_scene_configure,
    execute_scene_create_light,
    execute_scene_create_camera,
    execute_scene_create_empty,
)
```

## Runtime / Security Contract Notes

- keep the public `scene_create(...)` and `scene_configure(...)` tool names,
  action vocabularies, and structured response contracts stable
- preserve current coordinate parsing, default handling, and explicit error
  paths such as invalid coordinate payloads and unknown actions
- keep grouped render/color-management/world configuration aligned with the
  corresponding `scene_inspect(action=...)` contract shapes
- preserve current write-side `route_tool_call(...)` behavior and handler/RPC
  alignment while helpers move behind the facade

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_create_mega.py`
- `tests/unit/tools/scene/test_scene_configure_mega.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/e2e/tools/scene/test_scene_configure_roundtrip.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_create_mega.py tests/unit/tools/scene/test_scene_configure_mega.py tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/test_handler_rpc_alignment.py tests/unit/adapters/mcp/test_structured_contract_delivery.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/tools/scene/test_scene_configure_roundtrip.py -q`

## Docs To Update

- inherit parent docs closeout unless grouped create/configure ownership wording
  changes in `_docs/_MCP_SERVER/README.md` or
  `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- grouped `scene_create(...)` and `scene_configure(...)` helpers no longer live
  inline with the read-heavy context/inspect/snapshot branch inside `scene.py`
- public action names, defaults, structured payloads, and explicit error paths
  remain stable
- grouped render/color-management/world writes still track the same contract and
  roundtrip behavior
- focused unit/integration lanes plus configure roundtrip still prove no public
  mega-tool drift

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
- treat this as the write-side companion to `TASK-159-02-02` so the former
  mixed read/write leaf stays split into focused implementation passes
