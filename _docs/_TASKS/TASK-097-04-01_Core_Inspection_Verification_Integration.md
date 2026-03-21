# TASK-097-04-01: Core Inspection-Based Verification Integration

**Parent:** [TASK-097-04](./TASK-097-04_Inspection_Based_Verification_Integration.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-097-03](./TASK-097-03_Postcondition_Registry_for_High_Risk_Fixes.md), [TASK-089-02](./TASK-089-02_Structured_Scene_Context_and_Inspection_Contracts.md), [TASK-089-03](./TASK-089-03_Structured_Mesh_Introspection_Contracts.md)  

---

## Objective

Implement the core code changes for **Inspection-Based Verification Integration**.

---

## Repository Touchpoints

- `server/router/application/router.py`
- `server/router/application/engines/tool_correction_engine.py`
- `server/router/adapters/mcp_integration.py`
- `server/adapters/mcp/router_helper.py`

---

## Planned Work

- Implement the concrete leaf scope implied by the parent task in the listed touchpoints.
- Keep responsibilities aligned with Clean Architecture and `RESPONSIBILITY_BOUNDARIES.md`.
- Avoid introducing new bootstrap side effects outside the platform composition root.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-097-04-01-01](./TASK-097-04-01-01_Postcondition_Mapping_and_Verification_Trigger.md) | Postcondition Mapping and Verification Trigger | Core slice |
| [TASK-097-04-01-02](./TASK-097-04-01-02_Inspection_Call_Bridge_and_Result_Evaluation.md) | Inspection Call Bridge and Result Evaluation | Core slice |

---

## Acceptance Criteria

- high-risk verification depends on inspection-layer truth, not semantic guesswork
---

## Atomic Work Items

1. Map each high-risk correction family to the scene or mesh inspection contracts it needs for verification.
2. Trigger verification after correction and before final success is reported through adapter execution reports.
3. Keep verification logic dependent on inspection-layer truth rather than semantic confidence or prose heuristics.
