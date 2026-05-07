# TASK-160-01: Streamable HTTP visibility transaction audit and discovery churn regression

**Parent:** [TASK-160](./TASK-160_Guided_Client_Feedback_And_Streamable_HTTP_Recovery_UX.md)
**Status:** ✅ Done
**Priority:** 🔴 High
**Completed On:** 2026-05-07

**Completion Summary:** Added a per-session Streamable visibility transaction
guard plus `tools/list` audit middleware, made discovery visibility checks wait
for same-session refreshes, and added unit/integration regressions so guided
tool-surface churn can now be separated from client-side deferred-tool loss.

## Objective

Harden the Streamable HTTP guided runtime so `tools/list` and discovery-proxy
clients do not observe transient partial visibility while the server is
reapplying guided session visibility, and add enough runtime audit logging to
separate real repo-side tool-surface churn from client-side deferred-tool
disconnect narratives.

## Repository Touchpoints

| Path | Expected ownership | Why it is in scope |
|------|--------------------|--------------------|
| `server/adapters/mcp/guided_mode.py` | FastMCP visibility application seam | Owns the actual `reset_visibility()` + `enable/disable` transaction that can leak partial visibility to concurrent readers. |
| `server/adapters/mcp/visibility_runtime.py` | Session-scoped visibility barrier and audit seam | Owns the same-session serialization, lifecycle guardrails, and shaped-surface audit path introduced by this slice. |
| `server/adapters/mcp/session_capabilities_runtime_glue.py` | Session-state runtime glue | Calls the visibility application path whenever guided state changes. |
| `server/adapters/mcp/discovery/search_surface.py` | Discovery proxy seam | `call_tool(...)` and the public discovery visibility checks should wait for an in-flight same-session visibility refresh before trusting current visibility. |
| `server/adapters/mcp/factory.py` | FastMCP composition root | Owns middleware registration for `tools/list` audit / serialization. |
| `tests/e2e/integration/test_guided_streamable_spatial_support.py` | Streamable runtime proof lane | Should reproduce same-session guided visibility churn during spatial refresh and prove the stable list/discovery surface. |
| `tests/unit/adapters/mcp/` | Targeted adapter/runtime helper proof | Should cover the visibility-transaction helper or audit middleware contract without requiring Blender. |
| `README.md`, `_docs/_MCP_SERVER/README.md` | Product/runtime contract docs | Need one explicit note that Streamable guided visibility reapply is serialized against `list_tools()` so clients should not see partial surfaces. |

## Implementation Notes

- Introduce one per-session visibility transaction guard keyed by the active
  FastMCP session id.
- Use that guard in the guided visibility-application path so concurrent
  visibility refreshes do not overlap.
- Make `tools/list` wait for the in-flight visibility transaction before
  returning model-visible tools for the session.
- Record lightweight audit logs with:
  - session id
  - phase/current step
  - expected visible tool set after refresh
  - actual `tools/list` result
  - missing/unexpected tool names when the observed set diverges
- Preserve the existing async worker-thread contract for Blender-backed spatial
  reads; this task is about visibility-transaction stability and observability,
  not about reworking the spatial graph execution path itself.

## Runtime / Security Contract Notes

- This slice applies to session-aware FastMCP runtimes such as Streamable HTTP,
  where `tools/list`, `search_tools(...)`, or `call_tool(...)` can race with a
  same-session visibility refresh; it does not introduce a repo-global lock.
- This slice must not widen the public MCP surface or leak hidden internal tool
  names beyond the already visible public tool ids.
- Audit logs may include public tool names, session ids, guided step names, and
  visibility deltas, but must not log secrets, raw provider keys, or large
  payload bodies.
- `tools/list` serialization must stay bounded to the current session only; one
  client's visibility refresh must not block unrelated sessions.

## Validation Closeout Notes

- The follow-up review loop reran the repo-required broad lanes before the final
  closure commit: full unit tests, the Blender-backed E2E runner, and
  `pre-commit run --all-files --show-diff-on-failure`.
- The owner-lane commands below remain the focused proof for this slice and can
  still be used to reproduce the local visibility/runtime checks quickly.

## Tests To Add / Update

- Add a Streamable HTTP regression that creates a guided visibility transition
  and issues a concurrent `list_tools()` request while visibility reapply is
  intentionally slowed; the client must still receive a stable discovery/tool
  surface.
- Add narrow unit tests for the visibility transaction helper, the public
  discovery visibility checks used by `call_tool(...)`, and the middleware
  audit path so the lock-and-audit behavior stays deterministic without a full
  FastMCP server run.

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- Add one `_docs/_CHANGELOG/` entry for the Streamable guided visibility
  transaction audit and `tools/list` stability fix.

## Status / Board Update

- Kept `TASK-160` as the open umbrella.
- This narrow execution leaf is complete and does not need its own promoted
  board row under `_docs/_TASKS/README.md`.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_runtime.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_session_phase.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_server_factory.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_runtime.py tests/e2e/integration/test_guided_streamable_spatial_support.py -q`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`

## Acceptance Criteria

- Guided Streamable HTTP sessions no longer expose transient partial tool sets
  to concurrent `tools/list()` reads during visibility reapply.
- `call_tool(...)` and the public discovery visibility checks no longer trust
  visibility mid-refresh when a same-session guided transition is still being
  applied.
- Server logs make it possible to tell whether a future “tool disappeared”
  incident came from:
  - repo-side public `tools/list()` output changing
  - repo-side shaped-surface visibility mismatch
  - or client/harness deferred-tool churn despite a stable server surface.
