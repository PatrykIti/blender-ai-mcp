# 113 - 2025-12-15: Flexible vector/color parameter parsing (string `"[...]"` + list)

**Status**: ✅ Completed  
**Type**: Tooling UX / API Consistency  
**Task**: [TASK-064](../_TASKS/TASK-064_Flexible_List_Parameter_Parsing.md)

---

## Summary

Standardized “vector-like” and “color-like” MCP parameters so callers can pass either a real list (e.g. `[1, 2, 3]`) or a JSON-string form (e.g. `"[1, 2, 3]"`).

This reduces friction for LLM/tooling clients that sometimes serialize arrays as strings.

---

## Changes

- MCP:
  - `mesh_transform_selected`: `translate` / `rotate` / `scale` accept `list` or string `"[...]"` and are parsed via `parse_coordinate`.
  - `material_create`: `base_color` / `emission_color` accept `list` or string `"[...]"` and are parsed via `parse_coordinate`.
- Router metadata + docs updated to reflect accepted input forms.
- Tests: added focused unit coverage for MCP parsing behavior.

---

## Files Modified (high level)

- MCP:
  - `server/adapters/mcp/areas/mesh.py`
  - `server/adapters/mcp/areas/material.py`
- Router metadata:
  - `server/router/infrastructure/tools_metadata/mesh/mesh_transform_selected.json`
  - `server/router/infrastructure/tools_metadata/material/material_create.json`
- Tests:
  - `tests/unit/tools/mesh/test_mesh_transform_selected_mcp_parsing.py`
  - `tests/unit/tools/material/test_material_create_mcp_parsing.py`
- Docs:
  - `_docs/TOOLS/MESH_TOOLS_ARCHITECTURE.md`
  - `_docs/TOOLS/MATERIAL_TOOLS_ARCHITECTURE.md`
  - `_docs/AVAILABLE_TOOLS_SUMMARY.md`

---

## Validation

```bash
poetry run pytest -q tests/unit/tools/mesh/test_mesh_transform_selected_mcp_parsing.py tests/unit/tools/material/test_material_create_mcp_parsing.py
```

