# TASK-148: No-Auth HTTP MCP Client Compatibility And Auth Misclassification Recovery

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Product Reliability / Client Compatibility
**Estimated Effort:** Large
**Dependencies:** TASK-125, TASK-130

## Objective

Stabilize the repo's no-auth Streamable HTTP MCP path across real client
families so a session-aware local server is not misclassified as
OAuth-required during reconnect, discovery, or stale-client-state recovery.

This umbrella is intentionally broader than one Claude Code bug report.
The target surface is the repo's no-auth HTTP MCP product path as seen by:

- Claude Code / Claude Desktop
- Codex CLI / desktop-style Codex MCP consumers
- Gemini CLI / Gemini-compatible MCP consumers
- other clients that probe auth/discovery metadata during HTTP startup

## Business Problem

The repo intentionally supports a stateful no-auth HTTP MCP runtime. That
surface must remain truthful:

- if the server does not require OAuth, it should not be documented or shaped
  as though it does
- if a client loses its transport/session state, that must not silently mutate
  into a fake authentication problem

Current evidence shows one important failure mode:

- a no-auth HTTP MCP server can be reclassified client-side as
  `needs authentication`
- a later `authenticate` attempt then fails on `/register` or related OAuth
  routes because the server never claimed to implement them
- once a client stores partial auth state for that profile, later reconnects
  may stay poisoned even though the server itself still runs normally

This is a product compatibility problem, not just a session bug:

- a Claude-only workaround could misrepresent the repo to Codex, Gemini, or
  future clients
- a fake OAuth surface may repair one client while teaching other clients the
  wrong auth semantics
- a pure docs workaround would leave real operator sessions fragile

## Scope

This umbrella covers:

- a cross-client behavior matrix for no-auth HTTP MCP startup, reconnect,
  auth discovery, and stale-state recovery
- deterministic reproduction of auth-misclassification / `needs-auth`
  poisoning
- recovery policy for stale client-side auth state on no-auth servers
- a repo-side compatibility fix only if it preserves truthful auth semantics
  for other clients
- regression coverage and operator docs for the chosen fix

This umbrella does **not** cover:

- turning the local no-auth MCP runtime into a real OAuth product surface
  unless the matrix and policy work explicitly justify that move
- broad transport redesign beyond the supported `stdio` / `streamable` modes
- client-specific prompt hacks as the primary fix

## Success Criteria

- the repo has one explicit matrix for how major MCP clients behave against the
  no-auth HTTP path
- the current `needs-auth` / failed-`authenticate` incident is reproduced and
  categorized clearly as:
  - transport/session reset
  - stale auth-state poisoning
  - client auth-discovery misclassification
  - or genuine server auth behavior
- any adopted fix keeps the repo honest about auth support to clients that do
  not need OAuth
- operators have one bounded recovery path for poisoned local client auth state
- regression coverage proves the chosen behavior on the repo side

## Repository Touchpoints

- `server/adapters/mcp/factory.py`
- `server/adapters/mcp/server.py`
- `server/infrastructure/config.py`
- `scripts/run_streamable_openrouter.sh`
- `tests/e2e/integration/test_mcp_transport_modes.py`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/_TASKS/README.md`

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/e2e/integration/test_mcp_transport_modes.py`
- additional transport/client-compatibility coverage as determined by the
  reproduction slice

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when the umbrella ships

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-148-01](./TASK-148-01_Cross_Client_Matrix_And_Reproduction_Harness_For_No_Auth_HTTP_MCP.md) | Build the client matrix and deterministic reproduction path for the current no-auth HTTP incompatibility |
| 2 | [TASK-148-02](./TASK-148-02_Auth_State_Poisoning_And_Recovery_Policy_For_No_Auth_HTTP_Servers.md) | Define how stale client-side auth state is detected, cleared, or safely bypassed without lying about server auth semantics |
| 3 | [TASK-148-03](./TASK-148-03_Runtime_Compatibility_Fix_Regression_Pack_And_Docs.md) | Implement the chosen repo-side compatibility fix, then lock it in with tests and docs |

## Status / Board Update

- promoted as a new board-level open item because the issue spans transport,
  client compatibility, and runtime truthfulness rather than one local bugfix
- positioned as a follow-on after TASK-125 now that the repo already has an
  explicit `streamable HTTP` path to harden
