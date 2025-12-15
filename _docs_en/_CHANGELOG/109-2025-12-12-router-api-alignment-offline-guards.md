# 109 - 2025-12-12: Router API Alignment + Offline/Anti-Drift Guards

**Status**: ✅ Completed  
**Type**: Bug Fix / Documentation / Testing  
**Task**: [TASK-061](../_TASKS/TASK-061_Router_API_Alignment_and_Offline_Testing.md)

---

## Summary

Aligned Router (Supervisor) + tool metadata with the real MCP tool API, stabilized offline/unit-test behavior around LaBSE loading, and added a regression guard that fails fast when metadata drifts from MCP tool signatures.

---

## Changes

### Router ↔ MCP API alignment

- Updated router logic to use current MCP parameter names:
  - `mesh_bevel.offset` (was `width`)
  - `mesh_extrude_region.move` (was `depth`)
- Ensured dispatcher can execute router-emitted mega-tools (`mesh_select`, `mesh_select_targeted`).

### Offline / unit-test stability (LaBSE)

- Unified embedding model loading via shared DI provider (`get_labse_model()`), respecting:
  - pytest skip (`PYTEST_CURRENT_TEST`)
  - offline mode (`HF_HUB_OFFLINE` → `local_files_only`)
- Updated `vector_db_manage` to use the shared model provider and return a clear error when embeddings are unavailable (instead of attempting downloads/timeouts).

### Anti-drift guard (new test)

- Added a unit test that compares:
  - MCP tool definitions (`server/adapters/mcp/areas/*.py`) vs
  - router tool metadata (`server/router/infrastructure/tools_metadata/**/*.json`)
- The guard checks:
  - every `tool_name` in metadata exists in MCP tools
  - every metadata parameter key exists in the MCP function signature
  - router-emitted `tool_name="..."` string literals exist in MCP tools

### Docs sweep (router/workflows)

- Updated `_docs/_ROUTER` workflow docs to match current API (`offset`, `move`, no legacy `mesh_extrude`).

---

## Files Modified (high level)

- Runtime:
  - `server/adapters/mcp/areas/vector_db.py`
  - `server/router/infrastructure/tools_metadata/modeling/modeling_create_primitive.json`
  - `server/router/infrastructure/tools_metadata/scene/scene_list_objects.json`
  - `server/router/infrastructure/tools_metadata/text/text_create.json`
  - `server/router/infrastructure/tools_metadata/text/text_edit.json`
- Tests:
  - `tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py`
- Docs:
  - `_docs/_ROUTER/WORKFLOWS/creating-workflows-tutorial.md`
  - `_docs/_ROUTER/WORKFLOWS/yaml-workflow-guide.md`
  - `_docs/_ROUTER/WORKFLOWS/README.md`
  - `_docs/_ROUTER/WORKFLOWS/expression-reference.md`

---

## Validation

```bash
poetry run pytest tests/unit/router -q
```

