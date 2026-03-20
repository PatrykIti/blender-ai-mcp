# 121 - 2025-12-20: Workflow catalog import action

**Status**: ✅ Completed  
**Type**: Feature / Router / Workflows  
**Task**: TASK-075

---

## Summary

Added `workflow_catalog(action="import")` to load external YAML/JSON workflows into the server, refresh workflow registry and embeddings, and prompt for overwrite confirmation on name conflicts.

> **Note (2025-12-21):** Inline and chunked import support was added in [Changelog 125](./125-2025-12-21-workflow-catalog-inline-chunked-import.md).

---

## Changes

- Extended `workflow_catalog` MCP tool with `import` action and `filepath`/`overwrite` parameters.
- Added conflict detection across loader cache, filesystem, and vector store embeddings.
- Implemented overwrite behavior with stale file cleanup and embedding deletion.
- Reloaded workflow loader, registry, and embeddings after import.
- Updated docs to reflect the new action and workflow import flow.

---

## Files Modified (high level)

- MCP Server:
  - `server/adapters/mcp/areas/workflow_catalog.py`
  - `server/application/tool_handlers/workflow_catalog_handler.py`
  - `server/domain/tools/workflow_catalog.py`
  - `server/infrastructure/di.py`
- Docs:
  - `README.md`
  - `_docs/AVAILABLE_TOOLS_SUMMARY.md`
  - `_docs/_MCP_SERVER/README.md`
  - `_docs/_ROUTER/README.md`
  - `_docs/_ROUTER/IMPLEMENTATION/32-lance-vector-store.md`
  - `_docs/_TASKS/TASK-075_Workflow_Catalog_Import.md`
  - `_docs/_TASKS/README.md`
  - `_docs/_CHANGELOG/README.md`

---

## Validation

Not run (doc + tool surface updates only).
