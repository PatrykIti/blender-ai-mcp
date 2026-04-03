# 204. MCP transport mode switching and session diagnostics

Date: 2026-04-03

## Summary

Completed `TASK-125` by adding explicit MCP transport-mode selection for
`stdio` vs stateful `streamable` HTTP, plus product-visible session
diagnostics for guided/runtime debugging.

## What Changed

- added config/runtime support for:
  - `MCP_TRANSPORT_MODE=stdio`
  - `MCP_TRANSPORT_MODE=streamable`
- added streamable HTTP bootstrap settings:
  - `MCP_HTTP_HOST`
  - `MCP_HTTP_PORT`
  - `MCP_STREAMABLE_HTTP_PATH`
- updated MCP server startup so the same repo can boot either:
  - subprocess/stdio MCP
  - stateful Streamable HTTP MCP
- exposed `session_id` and `transport` on:
  - `router_set_goal(...)`
  - `router_get_status()`
  - `reference_compare_stage_checkpoint(...)`
  - `reference_iterate_stage_checkpoint(...)`
- added focused unit coverage for:
  - transport-mode bootstrap wiring
  - session diagnostics in guided/router/reference payloads
- updated README and MCP client config examples for the supported transport
  modes

## Why

The repo needed a practical way to compare `stdio` vs `streamable` runtime
behavior while debugging guided-session loss. Operators also needed product
payloads that expose the MCP session identifier directly instead of forcing
root-cause analysis through server logs alone.
