# TASK-075: Workflow Catalog Import (YAML/JSON)

## Goal
Enable importing external workflow YAML/JSON files into the MCP server without rebuilding Docker images, while preserving safety (no execution) and keeping router/vector-store state consistent.

## Context
The current workflow discovery tool (`workflow_catalog`) is read-only and only lists/searches workflows already present in `server/router/application/workflows/custom/`. This forces a rebuild or file copy into the image for new workflows, which slows iteration.

We need a safe, explicit import path that:
- reads a workflow definition from a user-provided file path,
- persists it into the server’s workflow directory,
- refreshes the router registry and embeddings,
- and asks for confirmation when a workflow with the same name already exists.

## Problem Statement
- Rebuilding Docker images to add workflows is slow and error-prone.
- Manually copying files into the container bypasses the tool ecosystem and does not update embeddings.
- Existing workflow name collisions can silently overwrite, creating hard-to-debug routing behavior.

## Non-Goals
- No remote download (HTTP/S3/Git) support.
- No execution of workflows or router goal setting.
- No background file watching or hot-reload daemon.
- No workflow merge or diffing; import is replace-or-skip only.

## Requirements

### Functional
1) Import a workflow from a local YAML/JSON file path.
2) Validate the workflow using existing `WorkflowLoader` rules.
3) Persist to the server’s custom workflow directory.
4) If a workflow with the same name exists (in loader cache, files, or vector store), ask for confirmation.
5) If `overwrite=true`, replace the workflow and remove stale embeddings.
6) If `overwrite=false`, skip import and return a `skipped` status.
7) After import, refresh:
   - `WorkflowLoader` cache
   - `WorkflowRegistry` custom definitions
   - `WorkflowIntentClassifier` embeddings (when available)

### Safety & UX
1) No workflow execution during import.
2) All results returned as JSON string via MCP tool.
3) Conflict confirmation handled through the same tool by `overwrite=true/false`.
4) Clear, actionable status values: `imported`, `needs_input`, `skipped`, `error`.

### Compatibility
- Must work whether LanceDB is available or using the in-memory vector store fallback.
- Must not require network access or external dependencies beyond current YAML/JSON parsing.

## Proposed API
Extend MCP tool `workflow_catalog` with an import action:

```
workflow_catalog(
  action="import",
  filepath="/abs/or/relative/path/to/workflow.yaml",
  overwrite=true|false|None
)
```

### Input Parameters
- `filepath` (required): path to YAML/JSON workflow file.
- `overwrite` (optional):
  - `None` → ask via `needs_input` if conflicts exist,
  - `true` → replace existing workflow + clear embeddings,
  - `false` → skip import if conflicts exist.

### Response Shape (JSON)
- `status`: `imported` | `needs_input` | `skipped` | `error`
- `workflow_name`: workflow name parsed from file
- `message`: human-readable status
- `conflicts`:
  - `definition_loaded`: boolean
  - `files`: list of existing paths
  - `vector_store_records`: integer count
- `saved_path`: path in custom workflows directory (if imported)
- `source_path`: original file path
- `overwritten`: boolean
- `removed_files`: list of deleted workflow files (when overwriting)
- `removed_embeddings`: count of deleted vector records
- `workflows_dir`: custom workflows directory
- `embeddings_reloaded`: boolean

### Status Matrix
| Status | When | Next Action |
|--------|------|-------------|
| `imported` | Workflow saved and caches refreshed | None |
| `needs_input` | Conflict detected and `overwrite` not provided | Call again with `overwrite=true` or `overwrite=false` |
| `skipped` | Conflict detected and `overwrite=false` | None |
| `error` | Validation or IO failure | Fix input file/path and retry |

### Interaction Examples
```
# First import
workflow_catalog(action="import", filepath="/tmp/chair.yaml")
-> {"status":"imported","workflow_name":"chair_workflow",...}

# Conflict without overwrite
workflow_catalog(action="import", filepath="/tmp/chair.yaml")
-> {"status":"needs_input","conflicts":{...}}

# Overwrite confirmed
workflow_catalog(action="import", filepath="/tmp/chair.yaml", overwrite=true)
-> {"status":"imported","overwritten":true,...}

# Skip on conflict
workflow_catalog(action="import", filepath="/tmp/chair.yaml", overwrite=false)
-> {"status":"skipped",...}
```

## Detailed Flow

### Import Happy Path
1) `workflow_catalog(action="import", filepath=...)`
2) `WorkflowLoader.load_file()` validates and parses the file
3) File is saved into custom workflows directory
4) Loader cache reloaded (`WorkflowLoader.reload()`)
5) Registry reloaded (`WorkflowRegistry.load_custom_workflows(reload=True)`)
6) Embeddings refreshed (`WorkflowIntentClassifier.load_workflow_embeddings(...)`)
7) Return `status: imported`

### Conflict Resolution
- Detect conflicts in three places:
  1) Loader cache (`WorkflowLoader.get_workflow(name)`)
  2) Files on disk (`<name>.yaml/.yml/.json`)
  3) Vector store IDs in namespace `WORKFLOWS`
- If conflicts exist and `overwrite` is `None` → return `needs_input`
- If `overwrite=false` → return `skipped`
- If `overwrite=true`:
  - remove existing workflow files (excluding the newly saved file)
  - delete matching vector store records (by ID prefix `workflow__*`)
  - reload loader + registry + embeddings

### Conflict Detection Details
- Loader cache uses `WorkflowLoader.get_workflow(name)`.
- Filesystem checks for `<name>.yaml`, `<name>.yml`, `<name>.json` in custom workflows dir.
- Vector store matches by exact ID or by prefix `workflow_name__*` (multi-embedding records).

### Data Consistency Guarantees
- Imports always run validation before persistence.
- Reloads happen after file save to ensure caches reflect disk state.
- Embedding refresh uses current loader output to avoid stale records.

## Edge Cases
- File does not exist → `error` with details
- Unsupported extension → `error`
- YAML invalid or missing required fields → `error`
- Workflow name has spaces → validation error from `WorkflowLoader`
- Multiple existing files with same name but different extensions
- Vector store unavailable → skip deletion with warning; still import

## Implementation Plan

### 1) Domain Interface
- Extend `IWorkflowCatalogTool` with `import_workflow(filepath, overwrite)`

### 2) Handler Implementation
- `WorkflowCatalogToolHandler.import_workflow()`
- Reuse `WorkflowLoader` for validation and persistence
- Inject `vector_store` (for conflict detection + deletion)
- Safe overwrite logic with explicit `overwrite` flag

### 3) MCP Adapter
- Add `action="import"` to `workflow_catalog` tool
- Accept `filepath`, `overwrite` args
- Return JSON with `needs_input` on conflict

### 4) DI Wiring
- Pass shared vector store into `WorkflowCatalogToolHandler`

### 5) Documentation
- Update MCP docs and tool summary
- Add task and changelog entries

## Integration Points
- `WorkflowLoader`: validation and persistence.
- `WorkflowRegistry`: reload custom definitions for router expansion.
- `WorkflowIntentClassifier`: refresh embeddings used in semantic matching.
- `LanceVectorStore`: delete old workflow embeddings on overwrite.

## Implementation Notes
- Use `Path(filepath).expanduser()` and keep paths local.
- Persist with `WorkflowLoader.save_workflow()` to ensure consistent structure.
- Maintain non-destructive behavior unless `overwrite=true`.
- Do not call `router_set_goal` or run workflow steps.

## Logging / Telemetry
- Log import status and conflicts via existing MCP context logging.
- Warnings for vector store failures or registry reload issues.

## Risks and Mitigations
- **Risk:** Overwrite deletes correct workflow by mistake.  
  **Mitigation:** require explicit `overwrite=true` and return `needs_input` by default.
- **Risk:** Vector store deletion misses records.  
  **Mitigation:** match both exact ID and prefix.
- **Risk:** YAML file saved with different extension than source.  
  **Mitigation:** preserve `.json` when source is JSON; default to `.yaml` otherwise.

## Open Questions (to revisit later)
- Should we allow importing multiple workflows from a directory?
- Should we support remote import (URL/Git) with explicit allowlist?
- Should we expose a dry-run validation mode?

## Acceptance Criteria
- `workflow_catalog(action="import", filepath=...)` works with valid YAML/JSON.
- Import updates loader cache, registry, and embeddings.
- Conflicting names return `needs_input` unless `overwrite` is provided.
- Vector store entries are removed on overwrite (when available).
- Documentation reflects new action and parameters.

## Test Plan (Manual)
1) **Valid import**
   - Use a minimal workflow YAML.
   - Expect `status: imported` and new file in custom workflows dir.
2) **Conflict prompt**
   - Import the same workflow again without `overwrite`.
   - Expect `status: needs_input` with conflicts listed.
3) **Skip path**
   - Import same workflow with `overwrite=false`.
   - Expect `status: skipped`.
4) **Overwrite path**
   - Import same workflow with `overwrite=true`.
   - Expect `status: imported`, old embeddings removed.
5) **Invalid YAML**
   - Expect `status: error`.

## Rollout / Rollback
- Safe to roll out immediately; import is opt-in.
- Rollback by removing `import` action and handler method.

## Files (Implementation)
- `server/domain/tools/workflow_catalog.py`
- `server/application/tool_handlers/workflow_catalog_handler.py`
- `server/adapters/mcp/areas/workflow_catalog.py`
- `server/infrastructure/di.py`

## Documentation Updates
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_ROUTER/README.md`
- `_docs/_ROUTER/IMPLEMENTATION/32-lance-vector-store.md`
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/README.md`
