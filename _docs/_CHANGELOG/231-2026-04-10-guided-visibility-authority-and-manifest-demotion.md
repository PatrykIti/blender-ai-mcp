# 231. Guided visibility authority and manifest demotion

Date: 2026-04-10

## Summary

Completed TASK-153 by making the guided runtime visibility model explicit and
single-sourced:

- `build_visibility_rules(...)` plus session state now remain the only runtime
  authority for `llm-guided`
- capability tags no longer carry `phase:*` runtime semantics on registered
  tools
- capability manifest data now preserves phase context as metadata-only
  `phase_hints`
- guided visibility diagnostics now derive capability visibility from the same
  runtime-visible tool membership that shapes the actual surface

## What Changed

- demoted capability phase tags in:
  - `server/adapters/mcp/visibility/tags.py`
  so runtime-facing tool tags now stay coarse (`audience:*`, `entry:*`) while
  phase context moves into metadata-only `CAPABILITY_PHASE_HINTS`
- extended manifest metadata in:
  - `server/adapters/mcp/platform/capability_manifest.py`
  with `phase_hints` and a helper exposing all known internal/public runtime
  tool names per capability
- updated discovery metadata in:
  - `server/adapters/mcp/discovery/tool_inventory.py`
  - `server/adapters/mcp/discovery/search_documents.py`
  so search/inventory can still benefit from phase-shaped catalog hints without
  depending on runtime tags for visibility
- added `materialize_visible_tool_names(...)` in:
  - `server/adapters/mcp/transforms/visibility_policy.py`
  and rebuilt guided diagnostics in:
  - `server/adapters/mcp/guided_mode.py`
  so `router_get_status().visibility_rules`, guided capability diagnostics, and
  the shaped runtime surface all tell the same visibility story
- updated operator-facing docs in:
  - `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
  - `_docs/_MCP_SERVER/README.md`
  to state explicitly that tags/manifest are metadata and not a second hidden
  runtime gate on `llm-guided`

## Why

The guided surface had already moved to a rule-driven FastMCP visibility model,
but the docs and diagnostics still left room for architectural drift:

- phase tags still looked like runtime authority
- capability visibility diagnostics could be read as manifest/tag-derived
- discovery metadata and runtime shaping were not documented as separate layers

This change makes the ownership split explicit in both code and docs before
more guided-surface policy waves land on top of it.

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_tool_inventory.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_provider_inventory.py tests/unit/adapters/mcp/test_surface_inventory.py tests/unit/adapters/mcp/test_server_factory.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py tests/e2e/integration/test_guided_streamable_spatial_support.py -q`
  - result on this machine: `1 passed, 2 skipped`
  - the skips were transport-backed scenarios gated by the local runtime/test environment
- `python3 -m compileall server/adapters/mcp`
