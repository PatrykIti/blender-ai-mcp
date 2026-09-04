# TASK-122-02-04-01: Public Naming Generalization For Ratio Repair

**Parent:** [TASK-122-02-04](./TASK-122-02-04_macro_adjust_relative_proportion.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

**Completion Summary:** The proportion-repair tool was generalized immediately from creature-biased public naming to `macro_adjust_relative_proportion`. The public parameter model was also generalized from `head/body` to `primary/reference`, so the tool fits non-creature use cases without relying on hidden internal semantics.

## Objective

Generalize the public naming and parameter model for the ratio-repair macro so
it works cleanly beyond creature-specific workflows.

## Repository Touchpoints

- `server/domain/tools/`
- `server/application/tool_handlers/`
- `server/adapters/mcp/areas/`
- `server/adapters/mcp/contracts/`
- `server/adapters/mcp/dispatcher.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/router/infrastructure/tools_metadata/`
- `tests/unit/`
- `tests/e2e/`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TASKS/README.md`

## Acceptance Criteria

- the public tool name is generic enough for non-creature use cases
- the public parameter model uses neutral cross-object terminology
- docs and tests are aligned with the generalized naming

## Status / Board Update

- this subtask is closed and already reflected in the renamed public tool surface
