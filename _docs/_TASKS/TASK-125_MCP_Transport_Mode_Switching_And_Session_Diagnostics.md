# TASK-125: MCP Transport Mode Switching and Session Diagnostics

**Priority:** 🔴 High  
**Category:** Product Reliability / Runtime Operations  
**Estimated Effort:** Large  
**Dependencies:** TASK-083, TASK-093, TASK-124  
**Status:** ✅ Done

**Completion Summary:** The MCP server now supports an explicit
`MCP_TRANSPORT_MODE` switch for `stdio` vs stateful `streamable` HTTP,
operator docs/config examples exist for both modes, and guided/router/reference
payloads now expose `session_id` plus `transport` so runtime session-loss
incidents can be traced directly from product payloads.

## Objective

Add a first-class transport-mode switch for the MCP server so local/runtime
operators can choose between:

- `stdio`
- `streamable`

while exposing explicit session identifiers in diagnostics and tool payloads so
session-loss problems can be traced across client reconnects, transport
switches, and runtime incidents.

## Business Problem

The current repo runs only one practical transport path: `stdio`.

That is simple, but it makes current session-loss failures harder to reason
about:

- runtime operators cannot quickly switch to `streamable HTTP` to isolate
  whether a problem is caused by subprocess/stdio lifecycle behavior
- guided/session-aware features such as:
  - `router_set_goal(...)`
  - `router_get_status()`
  - `reference_images(...)`
  - `reference_compare_stage_checkpoint(...)`
  - `reference_iterate_stage_checkpoint(...)`
  rely on MCP session state, but the visible product payloads do not surface
  enough transport/session diagnostics to explain when that state was reset
- when guided state disappears while the Blender scene still exists, operators
  currently have to infer whether the issue came from:
  - a client reconnect
  - a new MCP session
  - a new server process
  - or application logic

This is a runtime-observability problem and a transport-flexibility problem,
not just a prompt problem.

## Business Outcome

If this task is done correctly, the repo gains:

- one explicit config switch for selecting `stdio` vs `streamable`
- a transport bootstrap path that can be tested and reasoned about directly
- session diagnostics that make MCP session resets visible instead of implicit
- a cleaner operational path for comparing transport behavior when debugging
  guided-session failures
- a safer foundation for evaluating `streamable-stateless` later without mixing
  it into this first rollout

## Scope

This umbrella covers:

- transport-mode configuration for `stdio` and `streamable`
- server bootstrap/runtime wiring for both modes
- explicit session ID diagnostics in the current guided/router/reference
  surfaces
- docs and local client config examples for both supported modes
- regression coverage for transport selection and session-ID reporting

This umbrella does **not** cover:

- shipping `streamable-stateless` yet
- redesigning guided/reference session state to be stateless-safe
- adding external distributed state stores in this same wave
- replacing the current MCP surface model or session semantics

## Success Criteria

- one config value can select `stdio` or `streamable` transport mode
- the server can boot cleanly in both supported modes
- `router_get_status()` exposes a stable, explicit MCP session identifier
- recovery-facing guided/reference errors can include enough session
  diagnostics to distinguish state loss from Blender-scene loss
- docs and config examples explain how to run and debug both transport modes

## Repository Touchpoints

- `server/main.py`
- `server/infrastructure/config.py`
- `server/adapters/mcp/server.py`
- `server/adapters/mcp/factory.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/router.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/session_state.py`
- `tests/unit/adapters/mcp/`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/_TASKS/README.md`

## Completion Update Requirements

- add a `_docs/_CHANGELOG/*` entry and update `_docs/_CHANGELOG/README.md`
- update the MCP server/runtime docs and client config examples for both
  supported transport modes
- add focused regression coverage for transport selection and session
  diagnostics before considering the umbrella complete
- keep `_docs/_TASKS/README.md` and all child task statuses in sync

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-125-01](./TASK-125-01_Configurable_MCP_Transport_Mode_And_Bootstrap.md) | Add one explicit transport-mode config and bootstrap path for `stdio` vs `streamable` |
| 2 | [TASK-125-02](./TASK-125-02_Streamable_HTTP_Runtime_Path_And_Local_Client_Setup.md) | Wire and document the first supported `streamable HTTP` runtime path for local operators/clients |
| 3 | [TASK-125-03](./TASK-125-03_Session_ID_Diagnostics_And_Guided_Recovery_Visibility.md) | Surface explicit MCP session IDs and recovery diagnostics on guided/router/reference flows |
| 4 | [TASK-125-04](./TASK-125-04_Transport_Mode_Regression_Pack_And_Docs.md) | Validate both modes through tests, docs, and troubleshooting guidance |
