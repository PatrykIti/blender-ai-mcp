# TASK-167-02-03: Guided Flow And Router Debug Profile Instrumentation

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-167-02](./TASK-167-02_Runtime_Instrumentation_And_Targeted_Log_Routing.md)
**Objective:** Add bounded `guided_flow` and `router` debug instrumentation to the current guided-flow transition and router goal/status/logger seams so operators can trace step changes, refresh barriers, allowed-family changes, and router decision summaries directly from the Docker/server terminal.
**Repository Touchpoints:** `server/adapters/mcp/session_capabilities_flow.py`, `server/adapters/mcp/areas/router.py`, `server/router/infrastructure/logger.py`, `server/application/tool_handlers/router_handler.py`, `tests/unit/adapters/mcp/test_router_elicitation.py`, `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`, `tests/e2e/integration/test_guided_streamable_spatial_support.py`
**Acceptance Criteria:**
- `debug=guided_flow` surfaces step changes, `next_actions`, refresh barrier set/cleared moments, and allowed-family changes without printing large state dumps
- `debug=router` surfaces goal classification/no-match/needs-input/ready transitions and bounded router logger summaries through the existing router owner seams
- operators can correlate guided-flow transition logs with router goal/status logs from the same terminal output
- logs stay observational only and do not change router policy or guided-flow authority

## Current Owner / Likely Edit Map

| Path | Current owner seam | Likely edit anchors | Why this leaf owns it |
|------|--------------------|---------------------|-----------------------|
| `server/adapters/mcp/session_capabilities_flow.py` | `_default_next_actions_for_step(...)`, `_apply_spatial_refresh_gate(...)`, `_clear_spatial_refresh_gate(...)` | lines 633-760 | guided-flow step and refresh-barrier semantics are computed here |
| `server/adapters/mcp/areas/router.py` | `router_set_goal(...)`, `router_get_status(...)` | lines 424-552 | guided/reference state summaries are assembled here for MCP clients |
| `server/router/infrastructure/logger.py` | `RouterLogger` | lines 80-220 | router-owned console/event logging already converges here |
| `server/application/tool_handlers/router_handler.py` | goal classification helpers | lines 41-168 | router-side classification seams may need bounded debug markers at the application owner level |
| `tests/unit/adapters/mcp/test_guided_flow_state_contract.py` | guided-flow state proof lane | current step/refresh tests | guided-flow debug profile proof belongs on the state-contract owner lane |
| `tests/unit/adapters/mcp/test_router_elicitation.py` | router goal/status proof lane | current router-facing contract tests | router debug profile proof belongs on the router owner lane |
| `tests/e2e/integration/test_guided_streamable_spatial_support.py` | Streamable guided runtime proof lane | current refresh-barrier / router-status transport surface | integration proof for transition diagnostics lives here |

## Implementation Notes

- keep guided-flow logs delta-oriented:
  - old step -> new step
  - refresh barrier set/cleared
  - next actions changed
  - allowed families changed
- keep router logs bounded at the operator summary level rather than dumping
  the full router internals on every call
- if router logger gating is added, it should wrap the existing router logger
  owner rather than duplicating summary lines in unrelated modules

## Pseudocode

```python
if debug_scope_enabled("guided_flow"):
    logger.info("[GUIDED_FLOW_DEBUG] step=%s next_actions=%s allowed=%s", step, next_actions, allowed_families)

if debug_scope_enabled("router"):
    logger.info("[ROUTER_DEBUG] goal_status=%s workflow=%s unresolved=%d", status, workflow, unresolved_count)
```

## Runtime / Security Contract Notes

- no full prompt dumps, secret-bearing provider data, or unbounded state
  snapshots in normal logs
- debug logs must not alter router decision policy or guided-flow state

## Error Cases To Cover

- step change with refresh barrier set
- refresh barrier cleared after required checks complete
- `no_match` guided-manual goal path
- `needs_input` router clarification path
- router status payloads that already include guided/reference state but need
  bounded terminal diagnostics too

## Tests To Add/Update

- unit tests for profile-gated guided-flow and router summary markers
- focused integration coverage for refresh-barrier step changes over Streamable
  HTTP

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_DEV/README.md`

## Changelog Impact

- covered by the first `_docs/_CHANGELOG/*` entry that ships the `TASK-167`
  implementation family

## Status / Board Update

- remains nested under `TASK-167-02`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_router_elicitation.py -q`
- targeted Streamable proof after implementation where needed:
  - `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_streamable_spatial_support.py -q`

## Validation Category

- focused unit and Streamable integration tests
- `git diff --check`
