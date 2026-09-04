# 260. Guided partial macro and spatial-helper policy preservation

Date: 2026-04-25

## Summary

Fixed two guided-runtime correctness regressions on the `llm-guided` surface:

- routed partial macro reports that include an `error` now remain structured
  partial reports instead of being downgraded to empty failures
- pinned read-only spatial helpers remain callable while visible, even when the
  current guided flow step omits `spatial_context` from `allowed_families`

## What Changed

- in `server/adapters/mcp/areas/scene.py`:
  - added one shared macro-result finalizer for scene macro MCP adapters
  - validate routed macro dictionaries as `MacroExecutionReportContract` before
    falling back to adapter-side failed/blocked error envelopes
  - preserve valid `status="partial"` reports with `error`, `actions_taken`,
    `objects_modified`, verification recommendations, and follow-up flags
- in `server/adapters/mcp/router_helper.py`:
  - exempt the pinned read-only spatial support tools from guided family
    blocking while they remain part of the visible support surface
  - keep the fail-closed behavior for disallowed mutating families and unmapped
    guided mutators unchanged
- in focused unit tests:
  - covered routed `macro_attach_part_to_surface(...)` partial reports with an
    error payload
  - covered `scene_scope_graph(...)`, `scene_relation_graph(...)`, and
    `scene_view_diagnostics(...)` staying callable during a secondary-parts
    build step whose allowed families omit `spatial_context`

## Documentation

- updated `README.md` guided-runtime notes
- updated `_docs/_MCP_SERVER/README.md` macro report and `llm-guided` execution
  policy notes
- updated `_docs/LLM_GUIDE_V2.md` shipped spatial-baseline notes

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_macro_attach_part_to_surface_mcp.py tests/unit/adapters/mcp/test_context_bridge.py -q`
  - result on this machine: `34 passed`
- `PYTHONPATH=. poetry run pytest tests/unit -q`
  - result on this machine: `3095 passed`
- `poetry run ruff check server/adapters/mcp/areas/scene.py server/adapters/mcp/router_helper.py tests/unit/tools/scene/test_macro_attach_part_to_surface_mcp.py tests/unit/adapters/mcp/test_context_bridge.py`
  - result on this machine: passed
- `poetry run mypy server/adapters/mcp/areas/scene.py server/adapters/mcp/router_helper.py`
  - result on this machine: passed
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --files README.md _docs/LLM_GUIDE_V2.md _docs/_CHANGELOG/README.md _docs/_CHANGELOG/260-2026-04-25-guided-partial-macro-and-spatial-helper-policy.md _docs/_MCP_SERVER/README.md server/adapters/mcp/areas/scene.py server/adapters/mcp/router_helper.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/tools/scene/test_macro_attach_part_to_surface_mcp.py`
  - result on this machine: passed
