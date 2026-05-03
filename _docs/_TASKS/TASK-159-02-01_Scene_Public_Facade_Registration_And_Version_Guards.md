# TASK-159-02-01: Scene Public Facade, Registration, And Version Guards

**Parent:** [TASK-159-02](./TASK-159-02_Scene_MCP_Area_Modularization_And_Surface_Slices.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Stabilize the public `scene.py` facade, registration helpers, and version-policy
delivery before moving the named concern clusters into sibling modules.

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/providers/core_tools.py`
- `server/adapters/mcp/platform/capability_manifest.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_provider_versions.py`
- `tests/unit/adapters/mcp/test_surface_manifest.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Current Code Anchors

- `SCENE_PUBLIC_TOOL_NAMES`
- `register_scene_tools(...)`
- `_register_existing_tool(...)`
- `get_versioned_tool_versions(...)`

## Planned Code Shape

```python
def register_scene_tools(target):
    return {name: _register_existing_tool(target, name) for name in SCENE_PUBLIC_TOOL_NAMES}
```

## Runtime / Security Contract Notes

- keep public scene tool names, versions, tags, and manifest exposure stable
- do not let helper extraction drift public docstrings or hidden/public status
- preserve current provider inventory ordering and manifest runtime names

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_provider_versions.py`
- `tests/unit/adapters/mcp/test_surface_manifest.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_provider_inventory.py tests/unit/adapters/mcp/test_provider_versions.py tests/unit/adapters/mcp/test_surface_manifest.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`

## Docs To Update

- none directly unless `_docs/_MCP_SERVER/README.md` or
  `_docs/AVAILABLE_TOOLS_SUMMARY.md` needs ownership wording maintenance

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- scene public registration stays in one stable facade seam
- provider inventory, version-policy, and manifest tests prove no public surface
  drift
- later helper extraction can proceed without rediscovering the public contract

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
