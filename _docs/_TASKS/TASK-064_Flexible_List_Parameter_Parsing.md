# TASK-064: Flexible parsing for list/vector parameters (string `"[...]"` + list)

**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Category:** MCP API / UX Consistency  
**Estimated Effort:** Small  
**Created:** 2025-12-15  
**Completed:** 2025-12-15  
**Dependencies:** TASK-011-* (docstring standardization), TASK-061 (API alignment)

---

## Overview

Some MCP tools accept list/vector parameters strictly as `List[float]` (Pydantic), while other tools accept either a JSON list or a string form like `"[1, 2, 3]"` (parsed via `parse_coordinate`). This inconsistency causes avoidable validation errors and makes the API harder to use from LLM/tooling.

Observed examples:
- `mesh_transform_selected.scale` rejects string `"[1,1,0.5]"`.
- `material_create.base_color` rejects string `"[0.5,0.5,0.5,1.0]"`.

---

## Root Cause

- Several tool functions are typed as `Optional[List[float]]` (list-only) and do not apply `parse_coordinate(...)`.
- Docs/tooling often show string examples for vectors/colors, and some other tools already support both forms, so users naturally assume it works everywhere.

---

## Proposed Fix

Standardize “vector-like” and “color-like” parameters to accept both:

- `Union[str, List[float], None]` on the MCP tool signature.
- Parse using `parse_coordinate(...)` (or a dedicated `parse_color(...)` for RGBA if needed).

Start with the known offenders:
1. `mesh_transform_selected`: `translate`, `rotate`, `scale`
2. `material_create`: `base_color`, `emission_color`

Then (optional) audit other tools for similar mismatches.

---

## Acceptance Criteria

- [x] Both `scale=[1,1,0.5]` and `scale="[1,1,0.5]"` work for `mesh_transform_selected`.
- [x] Both `base_color=[..., ..., ..., ...]` and `base_color="[..., ..., ..., ...]"` work for `material_create`.
- [x] Docs + router metadata reflect the accepted forms consistently.

---

## Implementation Checklist

- [x] Update `mesh_transform_selected` tool signature to accept string + list and parse it.
- [x] Update `material_create` tool signature to accept string + list and parse it.
- [x] Add focused unit tests for MCP parsing.
- [x] Update router tools metadata for affected tools (type descriptions/examples).
- [ ] Audit other tools with list-only params and decide whether to standardize them too.

---

## Files to Modify

| Area | File | Change |
|------|------|--------|
| MCP | `server/adapters/mcp/areas/mesh.py` | `mesh_transform_selected`: accept `Union[str, List[float]]` + parse |
| MCP | `server/adapters/mcp/areas/material.py` | `material_create`: accept `Union[str, List[float]]` + parse |
| Utils | `server/adapters/mcp/utils.py` | Ensure parsing supports 3/4-length lists (if needed) |
| Router | `server/router/infrastructure/tools_metadata/mesh/mesh_transform_selected.json` | Update examples/types |
| Router | `server/router/infrastructure/tools_metadata/material/material_create.json` | Update examples/types |
| Tests | `tests/unit/...` | Add/adjust tests for parsing + metadata alignment |

---

## Documentation Updates Required (after completion)

| File | What to Update |
|------|----------------|
| `_docs/_TASKS/TASK-064_Flexible_List_Parameter_Parsing.md` | Mark ✅ Done + add completion date |
| `_docs/_TASKS/README.md` | Move task to ✅ Done + update statistics |
| `_docs/AVAILABLE_TOOLS_SUMMARY.md` | Make vector/color input forms consistent in examples |
| `_docs/TOOLS/MESH_TOOLS_ARCHITECTURE.md` | Clarify accepted forms for `mesh_transform_selected` |
| `_docs/TOOLS/MATERIAL_TOOLS_ARCHITECTURE.md` | Clarify accepted forms for `material_create` |
| `_docs/_CHANGELOG/*` | Add entry describing API/UX improvement |
