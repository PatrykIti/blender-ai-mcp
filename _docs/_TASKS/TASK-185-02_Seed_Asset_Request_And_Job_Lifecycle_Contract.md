# TASK-185-02: Seed Asset Request And Job Lifecycle Contract

**Parent:** [TASK-185](./TASK-185_Optional_Generative_3D_Seed_Asset_Intake.md)
**Status:** ⏳ To Do
**Priority:** 🟡 Medium
**Objective:** Define the typed request and async job lifecycle for optional seed-asset generation before wiring any provider-specific implementation.

**Repository Touchpoints:** `server/adapters/mcp/contracts/`, `server/application/tool_handlers/`, `server/adapters/mcp/areas/`, `server/infrastructure/config.py`, `tests/unit/adapters/mcp/`

## Implementation Notes

- Define provider-neutral request fields for prompt/reference inputs, output
  format, max wait time, and optional operator metadata.
- Define status states for queued, running, completed, failed, cancelled,
  timeout, and provider-unavailable.
- Preserve provider-specific response details behind normalized status/error
  fields.

## Runtime / Security Contract Notes

- reject unknown fields on strict public/provider contracts
- store only bounded job metadata and redact secrets/provider payloads
- enforce timeout and maximum artifact-size limits before download/import

## Tests To Add/Update

- unit tests for request validation, status transitions, timeout/failure states,
  and payload redaction
- compatibility tests for provider-unavailable and default-off behavior

## Docs To Update

- `_docs/_MCP_SERVER/README.md` if a public or guided surface is added
- `_docs/_TASKS/README.md` only if board state changes

## Acceptance Criteria

- provider-neutral request/status contracts exist before provider code depends on
  them
- failure and unavailable states are explicit and non-crashing
- provider-specific details cannot leak into public status payloads unbounded

## Validation Commands

- `git diff --check`
- targeted contract and lifecycle unit tests added by the implementation
