# TASK-148-03: Runtime Compatibility Fix, Regression Pack, And Docs

**Parent:** [TASK-148](./TASK-148_No_Auth_HTTP_MCP_Client_Compatibility_And_Auth_Misclassification_Recovery.md)
**Depends On:** [TASK-148-01](./TASK-148-01_Cross_Client_Matrix_And_Reproduction_Harness_For_No_Auth_HTTP_MCP.md), [TASK-148-02](./TASK-148-02_Auth_State_Poisoning_And_Recovery_Policy_For_No_Auth_HTTP_Servers.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Implement the chosen repo-side fix for no-auth HTTP MCP client compatibility only after the client matrix and auth-state policy are explicit, then lock the behavior in on the current FastMCP/platform and guided Streamable owner lanes.
**Repository Touchpoints:** `server/infrastructure/config.py`, `server/adapters/mcp/factory.py`, `server/adapters/mcp/server.py`, `tests/e2e/integration/_guided_surface_harness.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/integration/test_guided_surface_contract_parity.py`, `tests/e2e/integration/test_mcp_transport_modes.py`, `README.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`, `scripts/RUN_MCP_SERVER.md`, `_docs/_TASKS/README.md`
**Acceptance Criteria:**
- the selected fix is justified against the cross-client matrix, not only
  against Claude Code
- no-auth server semantics remain truthful in the public product docs
- the chosen repo-side fix names the exact FastMCP/platform seam it changed
  rather than defaulting to launcher-only work
- regression coverage protects the chosen behavior on the repo side across the
  guided Streamable and prompt-bridge surfaces
- docs explain the intended client behavior and any remaining known gaps

## Implementation Notes

- prefer the current FastMCP/platform shaping seams first:
  - `server/infrastructure/config.py`
  - `server/adapters/mcp/factory.py`
  - `server/adapters/mcp/server.py`
- only touch launcher/docs helpers after the repo-side behavior is explicit
- treat the OpenRouter launcher as operator documentation only; it is not the
  primary runtime seam for the no-auth compatibility fix
- keep the chosen fix bounded:
  - no fake OAuth routes
  - no client-specific hardcode unless the matrix proves there is no truthful
    generic alternative
  - no regression of prompt-capable versus tool-only client behavior without
    documenting the tradeoff explicitly

## Pseudocode

```python
matrix = load_task_148_matrix()
policy = load_task_148_recovery_policy()

if matrix.points_to_platform_shaping_issue:
    adjust_streamable_client_surface(config, factory)
elif matrix.points_to_runtime_bootstrap_issue:
    adjust_streamable_server_bootstrap(server)
else:
    raise RuntimeError("Matrix does not yet justify a repo-side compatibility fix")

run_guided_streamable_regressions()
update_operator_docs()
```

## Runtime / Security Contract Notes

- never repair the incident by falsely advertising OAuth support
- keep no-auth behavior truthful across tool-only and prompt-capable clients
- if the fix narrows prompt-bridge exposure, document the operator impact and
  keep the repo's supported client examples aligned

## Tests To Add/Update

- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_mcp_transport_modes.py`
- any focused unit coverage needed for `server/infrastructure/config.py`,
  `server/adapters/mcp/factory.py`, or `server/adapters/mcp/server.py`

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `scripts/RUN_MCP_SERVER.md`
- `_docs/_TASKS/README.md`

## Changelog Impact

- include in the parent umbrella changelog entry when shipped

## Status / Board Update

- remains nested under `TASK-148`
- owns the runtime closeout once the matrix and policy slices are complete

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_mcp_transport_modes.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`

## Validation Category

- implementation-ready transport/platform compatibility lane
- `git diff --check`
