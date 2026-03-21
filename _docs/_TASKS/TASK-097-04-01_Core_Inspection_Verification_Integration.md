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

### Slice Outputs

- implement inspection-triggered postcondition verification for high-risk correction paths
- ensure verification outcomes (pass/fail/inconclusive) are propagated through router execution contracts
- prevent optimistic success finalization when required inspection checks fail or are inconclusive

### Implementation Checklist

- touch `server/router/application/router.py` with explicit change notes and boundary rationale
- touch `server/router/application/engines/tool_correction_engine.py` with explicit change notes and boundary rationale
- touch `server/router/adapters/mcp_integration.py` with explicit change notes and boundary rationale
- touch `server/adapters/mcp/router_helper.py` with explicit change notes and boundary rationale
- add or update focused regression coverage for the slice behavior
- capture before/after evidence tied to the slice outputs

### Review Notes To Attach

- rationale per changed touchpoint and any explicit no-change decisions
- exact test commands and profile/config context used during validation
- deferred work list with safety rationale

---

## Acceptance Criteria

- verification is executed for registered high-risk postconditions before success is finalized
- verification outcomes are deterministic and visible in router execution reporting
- inconclusive or failed verification paths escalate according to policy instead of silent success
- integration preserves compatibility with existing low-risk correction flows

---

## Atomic Work Items

1. Implement verification trigger and outcome propagation in the listed router/adapters touchpoints.
2. Add tests for pass/fail/inconclusive verification branches with explicit expected contracts.
3. Capture before/after execution-report samples showing verification gating behavior.
4. Document verification trigger rules and compatibility notes for downstream audit exposure tasks.
