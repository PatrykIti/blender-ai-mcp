# TASK-148-02: Auth-State Poisoning And Recovery Policy For No-Auth HTTP Servers

**Parent:** [TASK-148](./TASK-148_No_Auth_HTTP_MCP_Client_Compatibility_And_Auth_Misclassification_Recovery.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define one explicit recovery policy for clients that store partial or stale
OAuth state against a no-auth HTTP MCP server.

## Repository Touchpoints

- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `README.md`

## Acceptance Criteria

- the repo explicitly distinguishes:
  - genuine auth-required servers
  - no-auth servers with poisoned client-side auth state
- the recovery path is documented for local operators
- the policy rejects fixes that would falsely advertise OAuth support to other
  MCP clients unless that tradeoff is explicitly approved by the parent task

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Tests To Add/Update

- none directly; this slice defines policy and operator recovery guidance

## Changelog Impact

- include in the parent umbrella changelog entry when shipped
