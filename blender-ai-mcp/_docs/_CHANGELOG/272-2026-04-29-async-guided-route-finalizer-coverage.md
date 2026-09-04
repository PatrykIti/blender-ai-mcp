# 272. Async guided route finalizer coverage

Date: 2026-04-29

## Summary

- moved async dirty modeling macros (`macro_cutout_recess(...)` and
  `macro_finish_form(...)`) onto the awaited async route helper so guided
  visibility refreshes complete before Streamable HTTP responses return
- moved async spatial graph/diagnostic variants onto the async route helper so
  Blender-backed scope, relation, and view-diagnostic reads stay off the
  Streamable HTTP event loop
- added regression coverage that the async macro and spatial helper variants do
  not call the sync route helper directly
- refreshed MCP docs to distinguish awaited async route/finalizer behavior from
  the sync visibility bridge

## Validation

- `poetry run pytest tests/unit/tools/modeling/test_macro_cutout_recess_mcp.py tests/unit/tools/modeling/test_macro_finish_form_mcp.py -q`
- `poetry run pytest tests/unit/adapters/mcp/test_scene_guided_scope_requirements.py -q`
- `poetry run pytest tests/unit/adapters/mcp/test_vision_macro_mcp_integration.py tests/unit/adapters/mcp/test_structured_contract_delivery.py::test_macro_cutout_recess_delivers_structured_content tests/unit/adapters/mcp/test_structured_contract_delivery.py::test_macro_finish_form_delivers_structured_content -q`
