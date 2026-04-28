# 269. Guided visibility and description finalizers

Date: 2026-04-28

## Summary

- reapplied FastMCP visibility after async guided-role registration so
  Streamable HTTP `list_tools()` reflects a flow step advanced by completed
  roles before the active tool response returns
- preserved original public scene-tool docstrings when registering async
  Streamable HTTP variants for visible guided spatial helpers
- added regression coverage for async role-registration visibility refresh and
  public descriptions on `scene_scope_graph(...)`,
  `scene_relation_graph(...)`, and `scene_view_diagnostics(...)`
- documented the async role-registration and public-docstring finalization
  contract for guided Streamable HTTP surfaces

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py::test_async_guided_role_hint_registration_reapplies_visibility tests/unit/adapters/mcp/test_search_surface.py::test_async_scene_spatial_tools_preserve_public_descriptions -q`
- `poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_search_surface.py -q`
- `poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/adapters/mcp/test_contract_docs.py tests/unit/adapters/mcp/test_platform_migration_docs.py -q`
- `poetry run ruff check server/adapters/mcp/session_capabilities.py server/adapters/mcp/areas/scene.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_search_surface.py`
- `poetry run ruff format --check server/adapters/mcp/session_capabilities.py server/adapters/mcp/areas/scene.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_search_surface.py`
- `git diff --check`
