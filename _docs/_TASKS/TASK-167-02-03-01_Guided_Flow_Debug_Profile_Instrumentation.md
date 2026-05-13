# TASK-167-02-03-01: Guided Flow Debug Profile Instrumentation

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-167-02-03](./TASK-167-02-03_Guided_Flow_And_Router_Debug_Profile_Instrumentation.md)
**Objective:** Add bounded `guided_flow` debug instrumentation to the current guided-flow state-shaping and persistence seams so operators can trace step changes, refresh barriers, required checks, and allowed-family changes directly from the Docker/server terminal.
**Repository Touchpoints:** `server/adapters/mcp/session_capabilities_flow.py`, `server/adapters/mcp/session_capabilities_registry.py`, `server/adapters/mcp/session_capabilities_bootstrap.py`, `server/adapters/mcp/session_capabilities_runtime_glue.py`, `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`, `tests/e2e/integration/test_guided_streamable_spatial_support.py`
**Acceptance Criteria:**
- `debug=guided_flow` surfaces step changes, `next_actions`, refresh barrier set/cleared moments, and allowed-family changes without printing large state dumps
- guided-flow transition logs are anchored to the real state-shaping and persistence owners, not only the default-value helper layer
- logs stay observational only and do not change guided-flow authority

## Current Owner / Likely Edit Map

| Path | Current owner seam | Likely edit anchors | Why this leaf owns it |
|------|--------------------|---------------------|-----------------------|
| `server/adapters/mcp/session_capabilities_flow.py` | `_default_next_actions_for_step(...)`, `_apply_spatial_refresh_gate(...)`, `_clear_spatial_refresh_gate(...)` | lines 633-760 | guided-flow default step and refresh semantics are computed here |
| `server/adapters/mcp/session_capabilities_registry.py` | `record_guided_flow_spatial_check_completion(...)`, `advance_guided_flow_from_iteration_async(...)` | lines 504-645 | live guided-flow completion and iteration transitions are applied here |
| `server/adapters/mcp/session_capabilities_bootstrap.py` | router-goal bootstrap and ready-session reference adoption | current router-goal/update seams | initial guided-flow state and pending-reference adoption are bootstrapped here |
| `server/adapters/mcp/session_capabilities_runtime_glue.py` | stale-state rearm and runtime persistence glue | current runtime-glue seams | guided-flow rearm and persistence are applied here |
| `tests/unit/adapters/mcp/test_guided_flow_state_contract.py` | guided-flow state proof lane | current step/refresh tests | guided-flow debug profile proof belongs on the state-contract owner lane |
| `tests/e2e/integration/test_guided_streamable_spatial_support.py` | Streamable guided runtime proof lane | current refresh-barrier transport surface | integration proof for transition diagnostics lives here |

## Implementation Notes

- keep logs delta-oriented:
  - old step -> new step
  - refresh barrier set/cleared
  - next actions changed
  - allowed families changed
- do not dump full session-state blobs into normal operator logs

## Pseudocode

```python
if debug_scope_enabled("guided_flow"):
    logger.info("[GUIDED_FLOW_DEBUG] step=%s next_actions=%s allowed=%s", step, next_actions, allowed_families)
```

## Runtime / Security Contract Notes

- no full prompt dumps or unbounded state snapshots in normal logs
- debug logs must not alter guided-flow state

## Error Cases To Cover

- step change with refresh barrier set
- refresh barrier cleared after required checks complete
- stale-state rearm after mutating tool paths

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- focused integration coverage for refresh-barrier step changes over Streamable
  HTTP

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
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py -q`
- final E2E/runtime proof for this leaf should be exercised through the
  repo-supported runner and the relevant updated integration coverage:
  - `poetry run python scripts/run_e2e_tests.py`

## Validation Category

- focused unit and Streamable integration tests
- `git diff --check`
