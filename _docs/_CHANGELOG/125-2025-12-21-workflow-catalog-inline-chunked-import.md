# Changelog 125 - 2025-12-21

## Added
- Inline workflow import for `workflow_catalog` (`content`, `content_type`, `source_name`).
- Chunked workflow import sessions (`import_init`, `import_append`, `import_finalize`, `import_abort`) for large payloads.

## Updated
- `WorkflowLoader` supports loading workflows from raw content.
- `WorkflowCatalogToolHandler` handles inline imports and chunked session state.
- MCP docs and task docs updated for new import paths.

## Files
- `server/router/infrastructure/workflow_loader.py`
- `server/domain/tools/workflow_catalog.py`
- `server/application/tool_handlers/workflow_catalog_handler.py`
- `server/adapters/mcp/areas/workflow_catalog.py`
- `tests/unit/tools/workflow_catalog/test_workflow_catalog_import.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_ROUTER/README.md`
- `_docs/_ROUTER/IMPLEMENTATION/32-lance-vector-store.md`
- `_docs/_TASKS/TASK-075_Workflow_Catalog_Import.md`

## Tests
- `poetry run pytest tests/unit/tools/workflow_catalog/test_workflow_catalog_import.py -q`
