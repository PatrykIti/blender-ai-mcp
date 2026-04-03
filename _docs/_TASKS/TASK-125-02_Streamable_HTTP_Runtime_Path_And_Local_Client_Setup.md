# TASK-125-02: Streamable HTTP Runtime Path and Local Client Setup

**Parent:** [TASK-125](./TASK-125_MCP_Transport_Mode_Switching_And_Session_Diagnostics.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** Added the first supported stateful `streamable HTTP`
runtime path plus local Docker/client config examples so operators can switch
between `stdio` and `streamable` intentionally during runtime debugging.

## Objective

Add the first supported `streamable HTTP` runtime path for local MCP usage and
document how to run it.

## Business Problem

If `streamable` is only added as an internal code path without operator-ready
docs/config examples, it will not help debugging real transport/session
problems.

The repo needs one usable local path that tells operators:

- how to boot the server in `streamable` mode
- which host/port/path settings matter
- how client examples differ from the current `stdio` / Docker subprocess path

## Technical Direction

Wire the server into a supported Streamable HTTP app/runtime and add the local
setup path to docs and client config examples.

Keep this leaf scoped to the stateful `streamable` path only.
Do **not** mix `streamable-stateless` into this first rollout.

## Repository Touchpoints

- `server/main.py`
- `server/adapters/mcp/server.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `README.md`

## Acceptance Criteria

- the repo can run in `streamable` mode with one documented local setup path
- client config examples exist for the supported `streamable` path
- the docs explicitly distinguish supported `streamable` from deferred
  `streamable-stateless`

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Tests To Add/Update

- bootstrap/runtime unit coverage as needed for the new mode

## Changelog Impact

- include in the parent task changelog entry when shipped
