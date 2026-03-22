# 127 - 2026-03-22: FastMCP 3.x test alignment after MCP server migration

## Summary

Aligned the unit test suite with the current FastMCP 3.x server model after the recent platform/runtime migration work.

This cleanup intentionally updated tests to the repo's current behavior instead of restoring old internal compatibility patterns:

- tests that previously assumed `tool.fn(...)` on plain MCP callables now use the callable directly
- `llm-guided` profile expectations now match the current search-first guided surface
- runtime inventory expectations now match the explicit task-capable dependency pair declared in project metadata

## Updated files

- `tests/unit/tools/material/test_material_create_mcp_parsing.py`
- `tests/unit/tools/mesh/test_mesh_select_mega.py`
- `tests/unit/tools/mesh/test_mesh_select_targeted_mega.py`
- `tests/unit/tools/mesh/test_mesh_transform_selected_mcp_parsing.py`
- `tests/unit/tools/scene/test_scene_create_mega.py`
- `tests/unit/adapters/mcp/test_client_profiles.py`
- `tests/unit/adapters/mcp/test_runtime_inventory.py`
- `server/adapters/mcp/platform/runtime_inventory.py`

## Validation

```bash
poetry run pytest tests/unit -q
```

Result:

- `2336 passed in 24.65s`
