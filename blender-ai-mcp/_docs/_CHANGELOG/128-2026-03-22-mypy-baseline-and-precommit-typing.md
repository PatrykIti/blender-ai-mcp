# 128 - 2026-03-22: Full-repo mypy baseline and pre-commit typing hook

## Summary

Added a repo-wide `mypy` baseline and wired it into the local `pre-commit` checks without changing the established RPC contract that allows `RpcResponse.result` to remain optional.

The cleanup intentionally respected the existing product/runtime semantics:

- `RpcResponse.result` stays `Optional[Any]` as part of the domain contract
- Python call sites were tightened to unwrap/validate RPC payloads explicitly instead of weakening the contract
- dynamic FastMCP/router/addon code paths received targeted casts/guards where static typing could not infer runtime guarantees on its own

## What Was Fixed For Mypy

- added a shared RPC result unwrapping helper for application tool handlers instead of returning raw `Optional[Any]` payloads directly
- normalized handler return types for `str`, `dict`, `list[dict]`, and `list[str]` payloads across scene/mesh/modeling/material/uv/system/extraction/armature/baking/text/collection/lattice/sculpt paths
- tightened `IRpcClient` typing so background-task methods are part of the visible interface and no longer look like ad hoc attributes to `mypy`
- fixed a large group of dynamic-args inference problems by explicitly typing request `args` dictionaries where values mix strings, numbers, vectors, and optionals
- aligned modeling/domain signatures where tuple defaults were previously declared as `list[float]`
- added null guards and narrowing helpers around optional runtime components such as RPC clients, LanceDB tables, TF-IDF vectorizers, and session awaitables
- cleaned up FastMCP/provider typing by making dynamic `LocalProvider` imports and factory-owned `_bam_*` metadata explicit to the type checker
- tightened workflow/router typing around dynamic workflow definitions, adaptation state, and ensemble matcher access
- fixed test doubles and test helper state so unit tests satisfy the same typed interfaces as production code
- moved legacy router metadata JSON/schema drift out of the typing pass and into a dedicated follow-up task instead of weakening the new Python typing baseline

This pass also introduced a dedicated follow-up backlog item for the older router metadata JSON/schema drift that still blocks the `check-router-tool-metadata` hook:

- [TASK-100](../_TASKS/TASK-100_Router_Metadata_Schema_Alignment.md)

## Updated files

- `.pre-commit-config.yaml`
- `pyproject.toml`
- `server/application/tool_handlers/_rpc_utils.py`
- `server/application/tool_handlers/*.py`
- `server/domain/interfaces/rpc.py`
- `server/domain/tools/modeling.py`
- `server/domain/tools/workflow_catalog.py`
- `server/adapters/mcp/**/*.py`
- `server/adapters/rpc/client.py`
- `server/infrastructure/config.py`
- `server/router/**/*.py`
- `blender_addon/**/*.py`
- `scripts/run_e2e_tests.py`
- `tests/unit/**/*.py`

## Validation

```bash
poetry run mypy
poetry run pytest tests/unit -q
PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run mypy --all-files
PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run ruff-check --all-files
```

Result:

- `mypy`: success, no issues in `536` source files
- unit tests: `2372 passed`
- `ruff-check`: passed

Residual note:

- full `pre-commit run --all-files` is still blocked by legacy router metadata/schema mismatches, now tracked in `TASK-100`
