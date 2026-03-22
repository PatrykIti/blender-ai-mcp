# TASK-097: Transparent Correction Audit and Postconditions

**Priority:** 🔴 High  
**Category:** Router Safety  
**Estimated Effort:** Medium  
**Dependencies:** TASK-089, TASK-095, TASK-096  
**Status:** ✅ Done

---

## Objective

Make router corrections explicit, inspectable, and verifiable so the system does not silently mutate intent or proceed after a correction that failed in practice.

---

## Problem

Even when an auto-correction is reasonable, two product risks remain:

- the client may not understand what was changed
- the server may assume the correction worked without validating the outcome

That is especially dangerous in Blender, where a correction can appear logically valid but still leave the scene in the wrong state.

Examples:

- mode changed but active object is still wrong
- selection was injected but not on the intended geometry
- a parameter was clamped and the shape is now materially different
- an override created a different feature than the user expected

Without transparency and postconditions, the system can drift while looking successful.

---

## Business Outcome

Turn correction into an auditable capability:

- what was changed
- why it was changed
- what confidence/rule caused it
- whether the expected postcondition actually became true

This improves trust, observability, and future tuning.

---

## Proposed Solution

Adopt a correction model that is:

- explicit
- explainable
- validated after execution for important paths

The product should distinguish between:

- correction intent
- correction execution
- postcondition verification

Risky or high-impact corrections should not be considered complete until the resulting scene state confirms the intended repair.

---

## Implementation Constraints

Follow [FASTMCP_3X_IMPLEMENTATION_MODEL.md](./FASTMCP_3X_IMPLEMENTATION_MODEL.md).

Audit and postcondition work should be layered on top of structured contracts and inspection truth.
Do not treat prose explanations as the primary audit record.

Runtime wiring rule:

- when introducing new runtime audit/verification collaborators, wire them explicitly through `server/infrastructure/di.py`
- avoid hidden adapter-level singleton construction for audit/postcondition services

---

## FastMCP Features / Approach Context

- **Structured response contracts** — **3.x baseline**  
  Use machine-readable correction and postcondition reporting.
- **Sampling structured output via `result_type`** — **FastMCP 2.14.1**  
  Useful for bounded internal audit/summary helpers.
- **Background Tasks** — **FastMCP 2.14.0**  
  Useful if validation becomes multi-step or expensive for larger jobs.

---

## Scope

This task covers:

- correction transparency
- structured correction reporting
- postcondition-based trust model for important fixes
- better visibility into why the router changed behavior

This task does not cover:

- full geometry QA for every operation
- replacing the existing router engines wholesale

---

## Why This Matters For Blender AI

An AI system that silently “fixes” things without proving the fix worked will eventually lose operator trust.

For this repo, strong correction UX should mean:

- the system is helpful
- the system is honest
- the system can be audited when it makes a bad call

That is especially important before the project adds more advanced workflow automation.

---

## Success Criteria

- Corrections are visible and explainable.
- Important corrections have explicit postconditions.
- The system is less likely to drift silently after a failed or misleading repair.
- Router behavior becomes easier to inspect, tune, and trust over time.

---

## Umbrella Execution Notes

This remains the umbrella task. The original scope stays unchanged.

### Atomic Delivery Waves

1. Define the correction event model.
2. Extend the base structured router execution report from TASK-089 with audit-oriented fields.
3. Register which fixes require post-execution verification.
4. Verify those fixes through inspection contracts.
5. Expose the audit trail in responses and logs.
6. Add regression coverage and docs for transparency behavior.

Implementation is decomposed into:

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-097-01](./TASK-097-01_Correction_Event_Model_and_Audit_Schema.md) | Define the correction audit event model |
| 2 | [TASK-097-02](./TASK-097-02_Router_Execution_Report_Pipeline.md) | Extend the base execution report with audit-aware reporting |
| 3 | [TASK-097-03](./TASK-097-03_Postcondition_Registry_for_High_Risk_Fixes.md) | Register postconditions for high-risk fixes |
| 4 | [TASK-097-04](./TASK-097-04_Inspection_Based_Verification_Integration.md) | Verify important fixes through inspection contracts |
| 5 | [TASK-097-05](./TASK-097-05_Audit_Exposure_in_MCP_Responses_and_Logs.md) | Expose audit trails to clients and logging |
| 6 | [TASK-097-06](./TASK-097-06_Correction_Audit_Tests_and_Documentation.md) | Add audit transparency coverage and docs |
