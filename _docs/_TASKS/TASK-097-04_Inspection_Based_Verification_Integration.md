# TASK-097-04: Inspection-Based Verification Integration

**Parent:** [TASK-097](./TASK-097_Transparent_Correction_Audit_and_Postconditions.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-097-03](./TASK-097-03_Postcondition_Registry_for_High_Risk_Fixes.md), [TASK-089-02](./TASK-089-02_Structured_Scene_Context_and_Inspection_Contracts.md), [TASK-089-03](./TASK-089-03_Structured_Mesh_Introspection_Contracts.md)

---

## Objective

Verify important corrections through structured scene and mesh inspection instead of optimistic assumptions.

---

## Active Runtime Seam

Primary runtime seam for router-aware MCP execution is:

- MCP area tools → `route_tool_call(...)` in `server/adapters/mcp/router_helper.py`

`server/router/adapters/mcp_integration.py` is a secondary middleware-style adapter path.
It should be kept behaviorally aligned where used, but runtime-critical verification behavior must be defined first on the primary `route_tool_call` path.

### Failure-Policy Rule

- surfaces that claim router-governed safety or verification must not silently downgrade to direct execution after router-processing failure
- any explicit compatibility fail-open mode must be reported as `bypassed_by_policy` (or equivalent) and must not claim verified router-correction semantics

---

## Atomic Work Items

1. Map each high-risk correction family to the inspection contracts it depends on.
2. Execute verification after correction and before success is finalized.
3. Add tests for verified success, verification failure, and inconclusive verification.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-097-04-01](./TASK-097-04-01_Core_Inspection_Verification_Integration.md) | Core Inspection-Based Verification Integration | Core implementation layer |
| [TASK-097-04-02](./TASK-097-04-02_Tests_Inspection_Verification_Integration.md) | Tests and Docs Inspection-Based Verification Integration | Tests, docs, and QA |

---

## Acceptance Criteria

- high-risk verification depends on inspection-layer truth, not semantic guesswork
- guided router-governed paths do not claim verified success after an undisclosed router bypass
