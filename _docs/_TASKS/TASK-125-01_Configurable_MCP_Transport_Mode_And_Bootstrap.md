# TASK-125-01: Configurable MCP Transport Mode and Bootstrap

**Parent:** [TASK-125](./TASK-125_MCP_Transport_Mode_Switching_And_Session_Diagnostics.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** Added explicit MCP transport bootstrap configuration
for `stdio` and `streamable`, with deterministic runtime validation and
bootstrap tests for both modes.

## Objective

Introduce one explicit transport-mode configuration for the MCP server and
bootstrap the runtime accordingly.

## Business Problem

Today the server boots through one implicit transport path, which makes it
hard to compare `stdio` behavior against `streamable HTTP` behavior during
runtime debugging.

Without one explicit mode switch:

- local operators cannot intentionally select the transport they want to test
- runtime docs/config examples drift into copy/paste variants instead of one
  canonical transport policy
- transport behavior is harder to validate in tests

## Technical Direction

Add one config value such as:

- `stdio`
- `streamable`

and wire server bootstrap so:

- `stdio` preserves the current default path
- `streamable` boots the HTTP path explicitly
- unsupported values fail early with a clear configuration error

## Repository Touchpoints

- `server/main.py`
- `server/infrastructure/config.py`
- `server/adapters/mcp/server.py`
- `server/adapters/mcp/factory.py`
- `tests/unit/adapters/mcp/`

## Acceptance Criteria

- one config field controls MCP transport mode
- `stdio` remains available as a supported path
- `streamable` becomes a supported path
- invalid transport mode values fail with a clear runtime/config error

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- transport/bootstrap unit coverage under `tests/unit/adapters/mcp/`

## Changelog Impact

- include in the parent task changelog entry when shipped
