# 323. TASK-160 Streamable visibility transaction audit and tools/list stability

Date: 2026-05-07

## Summary

- added `server/adapters/mcp/visibility_runtime.py` as the session-scoped owner
  for guided visibility transaction guards and `tools/list` audit logging
- serialized Streamable HTTP guided visibility reapply per MCP session so
  concurrent `tools/list()` reads wait for the active `reset_visibility()` /
  `enable_components()` rebuild to finish instead of observing a transient
  partial surface
- registered a FastMCP middleware in `server/adapters/mcp/factory.py` that:
  - waits for in-flight visibility refreshes before returning `tools/list`
  - compares the observed public tool set with the visibility policy expected by
    the current session state
  - logs missing or unexpected public tools when the runtime surface diverges
- hardened the guided discovery proxy in
  `server/adapters/mcp/discovery/search_surface.py` so `get_tool(...)`
  visibility checks also wait for same-session visibility refreshes
- expanded proof lanes with:
  - a unit test for middleware waiting on an in-flight visibility transaction
  - a Streamable regression that issues concurrent `guided_register_part(...)`
    and `list_tools()` calls while visibility rebuild is intentionally slowed
  - a session transcript-style regression that wrong-scope spatial checks do not
    collapse the discovery tools or pinned spatial helpers

## Runtime / Transport Contract

- This slice is session-scoped: it serializes only the active MCP session's
  visibility rebuild against same-session `tools/list` and discovery reads.
- The audit path logs expected-vs-observed public tool ids and guided step
  context only; it must not widen hidden-tool exposure or log secret-bearing
  payload bodies.
- The fix explains repo-side surface churn versus client/harness deferred-tool
  loss, but it does not redefine the broader guided client-feedback contract.

## Validation

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_runtime.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_session_phase.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_server_factory.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_runtime.py tests/e2e/integration/test_guided_streamable_spatial_support.py -q`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
