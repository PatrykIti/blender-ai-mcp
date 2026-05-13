# TASK-167-02: Runtime Instrumentation And Targeted Log Routing

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-167](./TASK-167_Cross_Module_Debug_Profile_Registry_And_Runtime_Logging.md)
**Objective:** Wire the shared debug profile registry into the current MCP runtime owners so each selected scope emits useful, bounded diagnostics to the Docker/server terminal for the exact repo-owned seams an operator is trying to debug.
**Repository Touchpoints:** `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/vision/reference_support.py`, `server/adapters/mcp/discovery/search_surface.py`, `server/adapters/mcp/visibility_runtime.py`, `server/adapters/mcp/session_capabilities*.py`, `server/adapters/mcp/areas/router.py`, `server/application/tool_handlers/router_handler.py`, `server/router/**`, `tests/unit/adapters/mcp/`, `tests/e2e/integration/`
**Acceptance Criteria:**
- `debug=vision` surfaces RU backend timing, optional support timing, and unavailable/blocked reasons without logging secrets or raw payloads
- `debug=reference` surfaces attach/list/remove/clear plus compare/iterate readiness transitions and key reference-id counts
- `debug=tools` surfaces `call_tool(...)` proxy resolution, argument canonicalization, and public-tool contract mismatches
- `debug=visibility`, `debug=guided_flow`, and `debug=router` each emit their own bounded runtime transitions without turning every other subsystem noisy
- the selected profiles write to the normal Docker/server terminal path so operators do not need a second custom log collector for standard debugging

## Implementation Notes

- reuse existing logger seams where they already exist, especially:
  - `visibility_runtime`
  - `search_surface` / `call_tool` proxy
  - router interception/firewall summaries
  - RU refresh and optional classifier/segmentation support
- avoid scattering raw `print(...)` statements; instrument through shared helpers
  and normal loggers so profile filtering stays consistent
- prefer explicit high-signal events over firehose dumps:
  - attach start/finish, RU refresh start/finish, elapsed time, reference count
  - optional classifier/segmentation invoked/skipped/timeout/unavailable
  - proxy compatibility normalization and hidden-tool recovery
  - guided-flow step change, refresh barrier set/cleared, required checks
- treat `ctx_info(...)` and logger output as complementary:
  client-facing guidance stays on MCP responses, operator debugging stays in logs

## Pseudocode

```python
if debug_scope_enabled("reference"):
    logger.info("[REFERENCE_DEBUG] attach_start goal=%s refs=%s", goal, count)

if debug_scope_enabled("vision"):
    logger.info("[VISION_DEBUG] ru_backend_start provider=%s ref_count=%s", provider, count)

if debug_scope_enabled("tools"):
    logger.info("[TOOLS_DEBUG] call_tool name=%s canonical_args=%s", name, canonical_keys)
```

## Runtime / Security Contract Notes

- debug messages must stay bounded and summary-level by default
- no provider secrets, auth headers, raw image bytes, or unconstrained local
  private paths in normal logs
- debug scopes must not change runtime behavior or authority; they are
  observational only
- third-party library noise should be opt-in and tied to one repo-owned scope
  only when it materially helps diagnosis

## Tests To Add/Update

- unit tests for profile-gated emission on current owner seams
- focused integration tests that enable one profile and assert the expected
  repo-owned log markers appear while unrelated markers stay absent
- regression tests for known operator failures such as proxy arg drift and RU
  attach/refresh timing attribution

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `README.md`

## Changelog Impact

- covered by the first `_docs/_CHANGELOG/*` entry that ships the `TASK-167`
  implementation family

## Validation Category

- focused unit/integration tests for gated logging behavior
- `git diff --check`
