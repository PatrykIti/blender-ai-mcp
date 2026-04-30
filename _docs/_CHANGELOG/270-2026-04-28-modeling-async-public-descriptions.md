# 270. Modeling async public descriptions

Date: 2026-04-28

## Summary

- preserved original public modeling-tool docstrings when registering async
  Streamable HTTP variants for `modeling_create_primitive(...)` and
  `modeling_transform_object(...)`
- kept guided `list_tools()` and `search_tools()` descriptions aligned with
  the public object-mode workflow and argument guidance instead of exposing
  async implementation notes
- added regression coverage for public descriptions on the async modeling
  tool registrations
- refreshed guided MCP docs to state that async spatial and modeling variants
  must keep their public descriptions

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_search_surface.py::test_async_modeling_tools_preserve_public_descriptions -q`
- `poetry run pytest tests/unit/adapters/mcp/test_search_surface.py -q`
- `poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/adapters/mcp/test_contract_docs.py tests/unit/adapters/mcp/test_platform_migration_docs.py -q`
- `poetry run pytest tests/unit -q`
- `poetry run ruff check server/adapters/mcp/areas/modeling.py tests/unit/adapters/mcp/test_search_surface.py`
- `poetry run ruff format --check server/adapters/mcp/areas/modeling.py tests/unit/adapters/mcp/test_search_surface.py`
- `git diff --check`
