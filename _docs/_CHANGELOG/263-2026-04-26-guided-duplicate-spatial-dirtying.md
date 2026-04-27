# 263. Guided duplicate spatial dirtying

Date: 2026-04-26

## Summary

Closed a guided spatial-state regression where successful object duplication
could leave active scope and relation facts marked fresh after the visible
workset changed.

## What Changed

- in `server/adapters/mcp/session_capabilities.py`:
  - added `scene_duplicate_object` to the deterministic guided
    spatial-dirtying tool set
  - re-arm spatial refresh for duplicate mutations the same way rename
    mutations re-arm, because both invalidate name/scope-bound facts
- in `server/adapters/mcp/router_helper.py`:
  - recognize successful direct `scene_duplicate_object(...)` stringified-dict
    results as successful mutations before marking guided spatial state stale
- in focused unit tests:
  - covered `scene_duplicate_object` through the direct stale-state helper
  - covered the routed successful `scene_duplicate_object(...)` path so the
    state changes only after a successful visible mutation

## Documentation

- updated `README.md` guided spatial dirtying notes
- updated `_docs/_MCP_SERVER/README.md` guided flow contract notes

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_context_bridge.py -q -k "scene_object_mutations_mark_guided_spatial_state_stale or successful_visible_mutation"`
  - result on this machine: `4 passed, 65 deselected`
- `poetry run ruff check server/adapters/mcp/session_capabilities.py server/adapters/mcp/router_helper.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_context_bridge.py`
  - result on this machine: passed
- `poetry run mypy server/adapters/mcp/session_capabilities.py server/adapters/mcp/router_helper.py`
  - result on this machine: passed
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --files README.md _docs/_MCP_SERVER/README.md _docs/_CHANGELOG/README.md _docs/_CHANGELOG/263-2026-04-26-guided-duplicate-spatial-dirtying.md server/adapters/mcp/session_capabilities.py server/adapters/mcp/router_helper.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_context_bridge.py`
  - result on this machine: passed
- `PYTHONPATH=. poetry run pytest tests/unit -q`
  - result on this machine: `3100 passed`
