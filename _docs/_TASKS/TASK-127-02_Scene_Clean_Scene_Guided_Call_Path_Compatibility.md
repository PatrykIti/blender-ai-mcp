# TASK-127-02: `scene_clean_scene` Guided Call-Path Compatibility

**Parent:** [TASK-127](./TASK-127_Guided_Utility_Public_Contract_Hardening_For_Scene_Clean_Scene.md)
**Status:** ✅ Done
**Priority:** 🔴 High

**Completion Summary:** The guided discovery `call_tool(...)` path now
canonicalizes legacy `keep_lights` / `keep_cameras` cleanup flags for
`scene_clean_scene(...)` when both values agree, and rejects mixed values with
one deterministic contract error that points clients back to the canonical
public flag.

## Objective

Implement the bounded compatibility/canonicalization path so guided utility
calls do not fail when older split cleanup flags are used on the public
surface.

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/platform/naming_rules.py`
- `server/adapters/mcp/transforms/public_params.py`
- `tests/unit/adapters/mcp/test_aliasing_transform.py`
- `tests/unit/adapters/mcp/test_search_surface.py`

## Acceptance Criteria

- guided cleanup calls succeed through the intended public path
- the implementation is bounded to this tool/contract problem and does not
  broaden unrelated handler signatures
- tests protect the chosen compatibility behavior

## Docs To Update

- `_docs/_MCP_SERVER/README.md` if public runtime behavior changes

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_aliasing_transform.py`
- `tests/unit/adapters/mcp/test_search_surface.py`

## Changelog Impact

- include in the parent task changelog entry when shipped
