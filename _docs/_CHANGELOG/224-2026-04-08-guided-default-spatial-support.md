# 224. Guided default spatial support

Date: 2026-04-08

## Summary

Completed TASK-149 by making `scene_scope_graph(...)`,
`scene_relation_graph(...)`, and `scene_view_diagnostics(...)` part of the
default visible `llm-guided` support set instead of leaving them as optional
on-demand helpers hidden behind the search-first surface.

## What Changed

- pinned the scene capability's spatial graph/view helpers into the default
  shaped `tools/list` surface for `llm-guided`
- updated guided visibility policy so the same tools stay enabled across
  bootstrap, build, inspect, and creature-handoff sessions
- updated README, MCP server docs, and prompt docs so the public contract now
  matches the runtime behavior
- extended unit and transport-backed guided surface regressions to prove:
  - spatial helpers are visible on the default shaped surface
  - creature handoff sessions keep them available
  - guided bootstrap/build benchmarks reflect the new surface size
- updated task files and the board in the same branch

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_guided_surface_benchmarks.py tests/e2e/integration/test_guided_surface_contract_parity.py -q`
- result: `53 passed`
- `poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- result: `11 passed`

## Why

The repo had already shipped the right spatial artifacts under TASK-143 and
TASK-144, but the guided product path still underused them in practice. This
change makes explicit 3D orientation support part of the normal `llm-guided`
working set so models do not have to guess anchor, relation, or view-space
state from screenshots and prose alone.
