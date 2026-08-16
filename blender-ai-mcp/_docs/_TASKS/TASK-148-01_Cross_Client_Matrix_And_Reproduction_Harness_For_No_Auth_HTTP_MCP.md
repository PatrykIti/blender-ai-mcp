# TASK-148-01: Cross-Client Matrix And Reproduction Harness For No-Auth HTTP MCP

**Parent:** [TASK-148](./TASK-148_No_Auth_HTTP_MCP_Client_Compatibility_And_Auth_Misclassification_Recovery.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Produce one explicit reproduction and evidence matrix for how major MCP clients
behave against the repo's no-auth Streamable HTTP server.

## Repository Touchpoints

- `tests/e2e/integration/test_mcp_transport_modes.py`
- `scripts/run_streamable_openrouter.sh`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- the repo documents which clients are in scope for this wave:
  - Claude Code / Claude Desktop
  - Codex CLI / desktop-style Codex consumers
  - Gemini CLI / Gemini-compatible MCP consumers
- the current `needs-auth` incident is reproduced with enough evidence to
  distinguish:
  - server process failure
  - session reset / reconnect
  - auth-state poisoning
  - client auth-discovery misclassification
- the reproduction notes include exact request/response evidence or client logs
  for any auth-discovery probes

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_TASKS/README.md` if promoted scope changes

## Tests To Add/Update

- extend or supplement `tests/e2e/integration/test_mcp_transport_modes.py`
  where repo-side reproduction coverage is feasible

## Changelog Impact

- include in the parent umbrella changelog entry when shipped
