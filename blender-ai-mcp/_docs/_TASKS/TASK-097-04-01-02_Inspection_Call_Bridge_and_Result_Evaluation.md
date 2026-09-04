# TASK-097-04-01-02: Inspection Call Bridge and Result Evaluation

**Parent:** [TASK-097-04-01](./TASK-097-04-01_Core_Inspection_Verification_Integration.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-097-03](./TASK-097-03_Postcondition_Registry_for_High_Risk_Fixes.md), [TASK-089-02](./TASK-089-02_Structured_Scene_Context_and_Inspection_Contracts.md), [TASK-089-03](./TASK-089-03_Structured_Mesh_Introspection_Contracts.md)  

---

## Objective

Implement the **Inspection Call Bridge and Result Evaluation** slice of the parent task.

---

## Repository Touchpoints

- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/areas/*.py`
- `server/router/adapters/mcp_integration.py` (secondary path parity)

---

## Planned Work

### Slice Outputs

- materialize structured execution/audit/postcondition behavior for correction paths
- ensure verification triggers map to inspection contracts for high-risk fixes
- expose auditable outcomes to responses/logs with deterministic fields

### Runtime Seam Rule

Primary runtime call bridge is `route_tool_call(...)` in `server/adapters/mcp/router_helper.py`.
Adjust `mcp_integration.py` only to preserve parity for middleware/explicit integration usage, not as the default execution seam.

### Implementation Checklist

- touch `server/adapters/mcp/router_helper.py` with explicit change notes and boundary rationale
- touch `server/adapters/mcp/areas/*.py` with explicit change notes and boundary rationale
- touch `server/router/adapters/mcp_integration.py` with explicit change notes and boundary rationale (parity scope)
- add or update focused regression coverage for the slice behavior
- capture before/after evidence tied to the slice outputs

### Review Notes To Attach

- rationale per changed touchpoint and any explicit no-change decisions
- exact test commands and profile/config context used during validation
- deferred work list with safety rationale

---

## Acceptance Criteria

- audit and execution-report fields are complete and deterministic
- postcondition verification gates high-risk success finalization
- failure/inconclusive verification paths are explicit and test-covered
- slice integrates with policy and contract layers without ambiguity

### Concrete DoD by Touchpoint

- `server/adapters/mcp/router_helper.py`
  - emits a structured execution report envelope with distinct sections for original call, correction steps, verification result, and final status
  - report distinguishes `verified_success`, `verification_failed`, and `verification_inconclusive`
  - fallback behavior is explicit and does not silently drop verification outcomes
- `server/adapters/mcp/areas/*.py`
  - router-aware entrypoints propagate structured report payloads instead of step-concatenated text-only output on structured surfaces
  - compatibility rendering for legacy text surfaces remains available
- `server/router/adapters/mcp_integration.py` (parity scope)
  - mirrors primary `route_tool_call` verification result semantics for middleware integration paths

---

## Atomic Work Items

1. Implement audit/report/verification mapping on the `route_tool_call` runtime path.
2. Add tests for success, failure, and inconclusive verification outcomes.
3. Capture before/after audit payload examples for corrected executions.
4. Document parity expectations for `mcp_integration.py` without shifting primary runtime ownership.
