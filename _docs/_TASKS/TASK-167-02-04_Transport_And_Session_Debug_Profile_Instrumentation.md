# TASK-167-02-04: Transport And Session Debug Profile Instrumentation

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-167-02](./TASK-167-02_Runtime_Instrumentation_And_Targeted_Log_Routing.md)
**Objective:** Add bounded `transport` debug instrumentation to the repo-owned `stdio` and Streamable HTTP bootstrap/session seams so operators can trace server startup, transport selection, session creation/reconnect behavior, and transport-mode mismatch issues from the normal Docker/server terminal.
**Repository Touchpoints:** `server/adapters/mcp/server.py`, `server/adapters/mcp/context_utils.py`, `server/adapters/mcp/areas/router.py`, `server/adapters/mcp/areas/reference.py`, `tests/unit/adapters/mcp/test_server_transport_mode.py`, `tests/e2e/integration/test_mcp_transport_modes.py`
**Acceptance Criteria:**
- `debug=transport` emits bounded transport bootstrap summaries for `stdio` and Streamable HTTP from the repo-owned MCP server entrypoint
- `debug=transport` emits bounded session/reconnect diagnostics that help explain transport churn without dumping unrelated runtime state
- the transport debug profile has explicit owner test lanes for unit bootstrap and runtime session behavior
- logs stay bounded and do not expose secrets or unbounded request payloads

## Current Owner / Likely Edit Map

| Path | Current owner seam | Likely edit anchors | Why this leaf owns it |
|------|--------------------|---------------------|-----------------------|
| `server/adapters/mcp/server.py` | `run(...)` | lines 34-75 | transport selection, startup logging, and reconnect-related top-level diagnostics are owned here |
| `server/adapters/mcp/context_utils.py` | `ctx_session_id(...)`, `ctx_transport_type(...)` | current response identity helpers | live session/transport identity also flows through these response-side helpers |
| `server/adapters/mcp/areas/router.py`, `server/adapters/mcp/areas/reference.py` | transport/session response surfaces | current session/transport response seams | transport diagnostics are also visible through current response builders here |
| `tests/unit/adapters/mcp/test_server_transport_mode.py` | transport bootstrap proof lane | lines 19-75 | direct unit lane for transport bootstrap ownership |
| `tests/e2e/integration/test_mcp_transport_modes.py` | transport runtime proof lane | lines 24-180 | direct runtime lane for `stdio` / Streamable session behavior |

## Implementation Notes

- keep `transport` narrow to repo-owned transport/session summaries:
  - selected transport mode
  - streamable host/port/path summary
  - session id creation/reconnect lifecycle where the repo already owns the seam
- do not turn this leaf into generic HTTP or third-party library tracing
- keep it compatible with the shared registry from `TASK-167-01` rather than
  adding separate transport-specific env vars

## Pseudocode

```python
if debug_scope_enabled("transport"):
    logger.info("[TRANSPORT_DEBUG] mode=%s host=%s port=%s path=%s", mode, host, port, path)
```

## Runtime / Security Contract Notes

- no secrets, auth headers, or unbounded request payload dumps in normal logs
- transport debug remains observational only and must not change bootstrap or
  reconnect behavior

## Error Cases To Cover

- invalid configured transport mode
- streamable bootstrap path mismatch
- session creation/reconnect transitions that need operator diagnosis

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_server_transport_mode.py`
- `tests/e2e/integration/test_mcp_transport_modes.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `README.md`

## Changelog Impact

- historical closeout entry ownership belongs to
  [TASK-167-03-02](./TASK-167-03-02_Debug_Profile_Docs_Board_Changelog_And_Final_Proof.md)

## Status / Board Update

- remains nested under `TASK-167-02`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_server_transport_mode.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_router_elicitation.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- final E2E/runtime proof for this leaf should be exercised through the
  repo-supported runner and the relevant updated transport integration coverage:
  - `poetry run python scripts/run_e2e_tests.py`

## Validation Category

- focused unit and transport runtime proof
- `git diff --check`
