# 124 - 2026-03-23: Router confirmation, workflow import, addon, and Docker runtime fixes

**Status**: ✅ Completed  
**Type**: Bugfix / Runtime Alignment  
**Task**: post-TASK-092 / post-TASK-094 stability follow-up

---

## Summary

Closed a small cluster of runtime and UX regressions discovered during real usage:

- Blender addon ZIP installs no longer fail on enable because package-relative imports are now used consistently inside the addon package.
- Docker image builds now complete again because the runtime dependency set includes `opentelemetry-sdk`, and prompt assets are copied into the container image.
- `workflow_catalog(import*)` adapter contracts now accept the richer import metadata returned by the handler.
- `router_set_goal` now consumes explicit `workflow_confirmation` answers instead of looping back to the same medium-confidence confirmation question.

---

## Changes

- Switched addon absolute imports from `blender_addon...` to package-relative imports in the packaged addon runtime.
- Added the missing `opentelemetry-sdk` runtime dependency and copied `_docs/_PROMPTS` into the Docker image.
- Expanded `WorkflowCatalogResponseContract` to cover import/finalize metadata such as `saved_path`, `source_path`, `overwritten`, removal stats, and chunk/session fields.
- Added a special confirmation-consumption path for `workflow_confirmation` before normal workflow parameter validation in `RouterToolHandler.set_goal(...)`.

---

## Files Modified (high level)

- Blender Addon:
  - `blender_addon/infrastructure/rpc_server.py`
  - `blender_addon/application/handlers/scene.py`
  - `blender_addon/application/handlers/system.py`
  - `blender_addon/application/handlers/extraction.py`
- MCP / Runtime:
  - `Dockerfile`
  - `pyproject.toml`
  - `server/adapters/mcp/contracts/workflow_catalog.py`
  - `server/application/tool_handlers/router_handler.py`
- Tests:
  - `tests/unit/router/application/test_router_contracts.py`
  - `tests/unit/tools/workflow_catalog/test_workflow_catalog_mcp_paths.py`
  - `tests/unit/router/application/test_router_handler_parameters.py`
  - `tests/unit/adapters/mcp/test_router_elicitation.py`

---

## Validation

- `poetry run pytest tests/unit/router/application/test_router_contracts.py tests/unit/tools/workflow_catalog/test_workflow_catalog_mcp_paths.py tests/unit/tools/workflow_catalog/test_workflow_catalog_assistants.py tests/unit/tools/workflow_catalog/test_workflow_catalog_import.py -q`
- `poetry run pytest tests/unit/router/application/test_router_handler_parameters.py tests/unit/adapters/mcp/test_router_elicitation.py -q`
- `./scripts/build_addon.py`
- `docker build -t blender-ai-mcp:local .`
