# TASK-167-02-03-02: Router Debug Profile Instrumentation

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-167-02-03](./TASK-167-02-03_Guided_Flow_And_Router_Debug_Profile_Instrumentation.md)
**Objective:** Add bounded `router` debug instrumentation to the current router goal/status/logger/audit seams so operators can trace goal classification, no-match/needs-input/ready transitions, and router execution summaries directly from the Docker/server terminal.
**Repository Touchpoints:** `server/adapters/mcp/areas/router.py`, `server/router/application/router.py`, `server/router/infrastructure/logger.py`, `server/adapters/mcp/router_helper.py`, `server/application/tool_handlers/router_handler.py`, `tests/unit/adapters/mcp/test_router_elicitation.py`, `tests/unit/router/application/test_router_handler_parameters.py`, `tests/unit/router/infrastructure/test_logger.py`, `tests/e2e/integration/test_guided_streamable_spatial_support.py`
**Acceptance Criteria:**
- `debug=router` surfaces goal classification/no-match/needs-input/ready transitions and bounded router logger summaries through the existing router owner seams
- router debug logs are anchored to the live logger/audit path and do not rely only on client-facing `ctx_info(...)`
- operators can correlate router goal/status logs with guided-flow transitions from the same terminal output

## Current Owner / Likely Edit Map

| Path | Current owner seam | Likely edit anchors | Why this leaf owns it |
|------|--------------------|---------------------|-----------------------|
| `server/adapters/mcp/areas/router.py` | `router_set_goal(...)`, `router_get_status(...)` | lines 364-552 | guided/reference state summaries are assembled here for MCP clients |
| `server/router/application/router.py` | live router logger usage | lines 114 and 1177-1207 | terminal-side router summaries are emitted from the real router instance here |
| `server/router/infrastructure/logger.py` | `RouterLogger`, especially `log_info(...)` and `log_execution_audit(...)` | lines 80-220 and 368-426 | router-owned console/event logging converges here, but relevant methods extend beyond the earlier narrow window |
| `server/adapters/mcp/router_helper.py` | execution-audit exposure | lines 559-570 | MCP-side audit exposure also contributes to terminal diagnostics |
| `server/application/tool_handlers/router_handler.py` | `set_goal(...)` and goal-shape classification path | lines 304+ | router-side application owner for goal resolution starts here |
| `tests/unit/adapters/mcp/test_router_elicitation.py` | router goal/status proof lane | current router-facing contract tests | router debug profile proof belongs on the router owner lane |
| `tests/unit/router/application/test_router_handler_parameters.py` | router handler owner lane | current goal-shape/handler tests | direct handler proof belongs here |
| `tests/unit/router/infrastructure/test_logger.py` | router logger owner lane | current RouterLogger tests | direct router logger proof belongs here |
| `tests/e2e/integration/test_guided_streamable_spatial_support.py` | Streamable runtime proof lane | current router-status transport surface | integration proof for router diagnostics lives here |

## Implementation Notes

- keep router logs bounded at operator summary level rather than dumping full
  router internals on every call
- if logger gating is added, wrap the existing router logger owner instead of
  duplicating summary lines in unrelated modules

## Pseudocode

```python
if debug_scope_enabled("router"):
    logger.info("[ROUTER_DEBUG] goal_status=%s workflow=%s unresolved=%d", status, workflow, unresolved_count)
```

## Runtime / Security Contract Notes

- no full prompt dumps, secret-bearing provider data, or unbounded state
  snapshots in normal logs
- debug logs must not alter router decision policy

## Error Cases To Cover

- `no_match` guided-manual goal path
- `needs_input` router clarification path
- router status payloads that already include guided/reference state but need
  bounded terminal diagnostics too

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/router/application/test_router_handler_parameters.py`
- `tests/unit/router/infrastructure/test_logger.py`
- focused integration coverage for router status summaries over Streamable HTTP

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_DEV/README.md`

## Changelog Impact

- historical closeout entry ownership belongs to
  [TASK-167-03-02](./TASK-167-03-02_Debug_Profile_Docs_Board_Changelog_And_Final_Proof.md)

## Status / Board Update

- remains nested under `TASK-167-02-03`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_router_elicitation.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/router/application/test_router_handler_parameters.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/router/infrastructure/test_logger.py -q`
- final E2E/runtime proof for this leaf should be exercised through the
  repo-supported runner and the relevant updated integration coverage:
  - `poetry run python scripts/run_e2e_tests.py`

## Validation Category

- focused unit and Streamable integration tests
- `git diff --check`
