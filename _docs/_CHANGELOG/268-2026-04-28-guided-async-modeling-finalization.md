# 268. Guided async modeling finalization

Date: 2026-04-28

## Summary

- fixed routed `modeling_transform_object(...)` guided finalization so corrected
  object identity is taken from the final successful modeling result instead of
  the original caller-supplied `name`
- ensured successful routed async transforms re-arm guided spatial state and
  guided-role convenience registration for the object that actually changed
- surfaced `guided_naming` warning payloads from native async modeling paths
  that consume raw router execution reports, including
  `modeling_create_primitive(...)` and `modeling_transform_object(...)`
- documented the async modeling finalization contract for Streamable HTTP and
  guided-role convenience registration
- added regression coverage for corrected transform identity, async spatial
  dirty-state rearm, guided-role registration, and naming-warning delivery

## Validation

- `poetry run pytest tests/unit/tools/test_mcp_area_main_paths.py -q`
- `poetry run pytest tests/unit/adapters/mcp/test_search_surface.py -q`
- `poetry run pytest tests/unit/adapters/mcp/test_context_bridge.py -q`
- `poetry run pytest tests/unit -q`
- `poetry run ruff check server/adapters/mcp/areas/modeling.py tests/unit/tools/test_mcp_area_main_paths.py`
- `poetry run ruff format --check server/adapters/mcp/areas/modeling.py tests/unit/tools/test_mcp_area_main_paths.py`
- `git diff --check`
