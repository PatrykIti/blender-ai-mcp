# TASK-148-03: Runtime Compatibility Fix, Regression Pack, And Docs

**Parent:** [TASK-148](./TASK-148_No_Auth_HTTP_MCP_Client_Compatibility_And_Auth_Misclassification_Recovery.md)
**Depends On:** [TASK-148-01](./TASK-148-01_Cross_Client_Matrix_And_Reproduction_Harness_For_No_Auth_HTTP_MCP.md), [TASK-148-02](./TASK-148-02_Auth_State_Poisoning_And_Recovery_Policy_For_No_Auth_HTTP_Servers.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Implement the chosen repo-side fix for no-auth HTTP MCP client compatibility
only after the client matrix and auth-state policy are explicit.

## Repository Touchpoints

- `server/adapters/mcp/factory.py`
- `server/adapters/mcp/server.py`
- `server/infrastructure/config.py`
- `tests/e2e/integration/`
- `README.md`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- the selected fix is justified against the cross-client matrix, not only
  against Claude Code
- no-auth server semantics remain truthful in the public product docs
- regression coverage protects the chosen behavior on the repo side
- docs explain the intended client behavior and any remaining known gaps

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- transport/client-compatibility regression coverage determined by the matrix

## Changelog Impact

- include in the parent umbrella changelog entry when shipped
