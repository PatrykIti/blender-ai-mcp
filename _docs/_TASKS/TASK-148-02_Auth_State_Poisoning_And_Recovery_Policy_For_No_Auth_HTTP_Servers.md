# TASK-148-02: Auth-State Poisoning And Recovery Policy For No-Auth HTTP Servers

**Parent:** [TASK-148](./TASK-148_No_Auth_HTTP_MCP_Client_Compatibility_And_Auth_Misclassification_Recovery.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Define one explicit recovery policy for clients that store partial or stale OAuth state against a no-auth Streamable HTTP MCP server, without changing the repo into a fake OAuth surface.
**Repository Touchpoints:** `README.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`, `scripts/RUN_MCP_SERVER.md`, `server/infrastructure/config.py`, `server/adapters/mcp/factory.py`
**Acceptance Criteria:**
- the repo explicitly distinguishes:
  - genuine auth-required servers
  - no-auth servers with poisoned client-side auth state
- the recovery path is documented for local operators on the supported
  Streamable launcher/doc surface
- the policy rejects fixes that would falsely advertise OAuth support to other
  MCP clients unless that tradeoff is explicitly approved by the parent task
- the policy states when prompt-bridge toggles are relevant versus irrelevant
  to the auth-misclassification incident

## Implementation Notes

- keep this slice policy-first and repo-truth-first:
  - no fake `/register`
  - no fake `authenticate`
  - no hidden “pretend OAuth” compatibility layer
- document the decision tree for:
  - fresh client profile
  - stale local auth cache
  - reconnect after a previous failed auth probe
  - tool-only versus prompt-capable client path
- align the operator recovery wording with the supported launcher/docs path:
  - `scripts/run_mcp_server.py`
  - `scripts/RUN_MCP_SERVER.md`
  - README + MCP server docs
- explicitly record whether `MCP_PROMPTS_AS_TOOLS_ENABLED` changes client
  startup behavior, but do not present that knob as an auth feature

## Pseudocode

```text
if server_is_no_auth and client_cache_is_poisoned:
    tell_operator_to_clear_local_client_auth_state
    retry_against_same_no_auth_profile
elif server_is_no_auth and client_reprobes_auth:
    record_probe_behavior_for_matrix
    keep repo docs truthful about no-auth semantics
else:
    follow the genuine auth-required server path
```

## Runtime / Security Contract Notes

- recovery guidance must never instruct the repo to claim OAuth support it does
  not implement
- operator docs must distinguish local client cache cleanup from server-side
  credential rotation or auth provisioning
- do not publish real client cache paths or tokens in repo docs unless they are
  safe, bounded, and already public

## Tests To Add/Update

- no direct runtime test ownership in this policy slice
- if policy wording changes client-facing surface behavior, reflect that in:
  - `tests/e2e/integration/test_guided_surface_contract_parity.py`
  - `tests/e2e/integration/test_guided_gate_state_transport.py`

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `scripts/RUN_MCP_SERVER.md`

## Changelog Impact

- include in the parent umbrella changelog entry when shipped

## Status / Board Update

- remains nested under `TASK-148`
- should close before the runtime-fix slice publishes operator recovery steps

## Validation Commands

- `git diff --check`
- targeted consistency grep for:
  - `/register`
  - `authenticate`
  - `MCP_PROMPTS_AS_TOOLS_ENABLED`
  - `streamable`

## Validation Category

- policy/docs drift repair
- `git diff --check`
