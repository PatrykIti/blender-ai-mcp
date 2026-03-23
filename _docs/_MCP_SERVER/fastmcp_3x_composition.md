# FastMCP 3.x Composition Model

Composition reference for the FastMCP 3.x migration baseline.

This document describes the runtime shape introduced by `TASK-083-02` through `TASK-083-05` and protected by the regression harness in `TASK-083-06`.

## Current Composition Root

The MCP server now boots through an explicit factory path:

- `server/adapters/mcp/factory.py`
- `server/adapters/mcp/surfaces.py`
- `server/adapters/mcp/settings.py`
- `server/adapters/mcp/platform/capability_manifest.py`

`server/adapters/mcp/server.py` is no longer the place that composes the tool surface directly.
It delegates to `build_server(surface_profile=...)`.

## Provider Groups

Current provider groups:

- `core_tools`
  - scene, mesh, modeling, material, uv, collection, curve, lattice, sculpt, baking, text, armature, system, extraction
- `router_tools`
  - `router_*`
- `workflow_tools`
  - `workflow_catalog`
- `internal_tools`
  - reserved for internal/helper-only platform capabilities

Area modules now expose `register_*_tools(target)` seams so the same tool definitions can be mounted on a `FastMCP` server or a `LocalProvider`.
The old `server/adapters/mcp/instance.py` decorator shim has been removed; runtime composition is now factory/provider based only.

## Surface Profiles

Current bootstrap-time surface profiles:

- `legacy-flat`
- `llm-guided`
- `internal-debug`
- `code-mode-pilot`

At this stage the profile matrix is intentionally conservative:

- `legacy-flat` and `llm-guided` share the same manifest and transform scaffold
- `internal-debug` and `code-mode-pilot` keep room for extra provider/debug capacity
- contract versioning is still deferred to later work (`TASK-091`)

## Transform Pipeline

The transform chain now has one explicit ordered scaffold:

1. `version_filter`
2. `naming`
3. `prompts_bridge`
4. `visibility`
5. `discovery`

At the current baseline, these stages are mostly placeholders.
That is intentional: `TASK-083-04` establishes the one canonical order first, and later tasks populate individual stages instead of bypassing the pipeline ad hoc.

## Context And Execution Bridge

The adapter layer now has reusable bridge primitives for:

- session-scoped state access
- execution context objects
- execution reports
- legacy string rendering for backward-compatible tool outputs

Key files:

- `server/adapters/mcp/session_state.py`
- `server/adapters/mcp/execution_context.py`
- `server/adapters/mcp/execution_report.py`
- `server/adapters/mcp/context_utils.py`
- `server/adapters/mcp/router_helper.py`

## Regression Harness

Current platform regression entry points:

- `tests/unit/adapters/mcp/test_runtime_inventory.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_server_factory.py`
- `tests/unit/adapters/mcp/test_transform_pipeline.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/unit/adapters/mcp/test_surface_bootstrap.py`
- `tests/unit/adapters/mcp/test_surface_inventory.py`
- `tests/unit/adapters/mcp/test_surface_compatibility.py`

Recommended command:

```bash
poetry run pytest \
  tests/unit/adapters/mcp/test_context_bridge.py \
  tests/unit/adapters/mcp/test_provider_inventory.py \
  tests/unit/adapters/mcp/test_runtime_inventory.py \
  tests/unit/adapters/mcp/test_server_factory.py \
  tests/unit/adapters/mcp/test_surface_bootstrap.py \
  tests/unit/adapters/mcp/test_surface_inventory.py \
  tests/unit/adapters/mcp/test_surface_compatibility.py \
  tests/unit/adapters/mcp/test_transform_pipeline.py \
  tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py \
  tests/unit/router/adapters/test_mcp_integration.py -q
```

Latest closure validation:

- command above passes on the current baseline
- latest local result: `88 passed`
- closure expectation met: `100%` pass rate with `0` side-effect bootstrap paths and `0` global-singleton area imports
