# TASK-103: Coverage Expansion for Scene MCP Area, Workflow Catalog, Lance Store, and RPC Server

**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-102](./TASK-102_Coverage_Expansion_For_Extraction_System_And_Scripts.md)

---

## Objective

Finish the next high-value coverage wave by targeting four remaining modules that still had a strong cost-to-benefit ratio:

- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/areas/workflow_catalog.py`
- `server/router/infrastructure/vector_store/lance_store.py`
- `blender_addon/infrastructure/rpc_server.py`

---

## Repository Touchpoints

- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/workflow_catalog/test_workflow_catalog_mcp_paths.py`
- `tests/unit/router/infrastructure/vector_store/test_lance_store_edge_cases.py`
- `tests/unit/adapters/rpc/test_rpc_server_edge_cases.py`
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TESTS/README.md`

---

## Planned Work

- add broad MCP wrapper tests for `scene` direct-execution helper paths
- add MCP workflow catalog tests for validation branches and background finalize flow
- add vector-store tests for LanceDB error/fallback branches
- add addon RPC server tests for background lifecycle edge cases and socket/error handling
- rerun full unit suite, repo coverage, and `pre-commit`

## Acceptance Criteria

- the selected modules show measurable coverage improvements
- the full unit suite stays green
- `pre-commit run --all-files` stays green
- docs reflect the new repo-wide test count and coverage baseline

## Completion Summary

- added focused unit tests for:
  - scene MCP wrappers and helper dispatch paths
  - workflow catalog validation/background-finalize MCP paths
  - LanceDB vector store edge/error/fallback branches
  - addon RPC server edge cases and background lifecycle plumbing
- full unit suite increased to `2436` passing tests
- repo-wide coverage (`server + blender_addon + scripts`) increased to `76%`
- targeted improvements from this batch:
  - `server/adapters/mcp/areas/scene.py`: `56% -> 74%`
  - `server/adapters/mcp/areas/workflow_catalog.py`: `64% -> 76%`
  - `server/router/infrastructure/vector_store/lance_store.py`: `56% -> 73%`
  - `blender_addon/infrastructure/rpc_server.py`: `60% -> 76%`

## Validation

```bash
poetry run pytest tests/unit -q
poetry run pytest tests/unit -q --cov=server --cov=blender_addon --cov=scripts --cov-report=term-missing:skip-covered
PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files
```
