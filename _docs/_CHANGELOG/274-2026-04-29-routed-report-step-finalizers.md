# 274. Routed report step finalizers

Date: 2026-04-29

## Summary

- changed async guided modeling finalizers to derive successful
  `modeling_create_primitive(...)` and `modeling_transform_object(...)`
  mutations from structured `report.steps` instead of parsing rendered legacy
  route text
- changed async `scene_clean_scene(...)` finalization to detect successful
  cleanup from routed report steps, so corrected multi-step cleanup routes still
  reset guided spatial freshness
- kept legacy route text rendering as the returned MCP result while using the
  structured report only for guided state and role-registration decisions
- added regression coverage for non-parseable legacy text and corrected
  multi-step cleanup reports

## Validation

- `poetry run pytest tests/unit/tools/test_mcp_area_main_paths.py -q`
- `poetry run pytest tests/unit/adapters/mcp/test_context_bridge.py -q`
- `poetry run pytest tests/unit/adapters/mcp/test_search_surface.py -q`
- `poetry run ruff format --check server/adapters/mcp/areas/modeling.py server/adapters/mcp/areas/scene.py tests/unit/tools/test_mcp_area_main_paths.py`
- `poetry run ruff check server/adapters/mcp/areas/modeling.py server/adapters/mcp/areas/scene.py tests/unit/tools/test_mcp_area_main_paths.py`
- `git diff --check`
