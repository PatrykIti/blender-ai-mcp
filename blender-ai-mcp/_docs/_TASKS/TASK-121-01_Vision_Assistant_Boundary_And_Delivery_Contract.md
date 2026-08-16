# TASK-121-01: Vision Assistant Boundary and Delivery Contract

**Parent:** [TASK-121](./TASK-121_Goal_Aware_Vision_Assist_And_Reference_Context.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** The reusable result envelope from `TASK-121-01-01` is now
in place, including richer optional fields for shape/proportion/correction
semantics, and `TASK-121-01-02` now adds explicit policy metadata so the
vision layer is carried as interpretation-only rather than truth or router
authority.

---

## Objective

Define the result contract, lifecycle, and product boundary for the lightweight
vision-assist layer before integrating it into macro/workflow execution.

---

## Repository Touchpoints

- `server/adapters/mcp/sampling/`
- `server/adapters/mcp/contracts/`
- `server/adapters/mcp/areas/`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `tests/unit/adapters/mcp/`

---

## Leaf Breakdown

| Leaf | Purpose |
|------|---------|
| [TASK-121-01-01](./TASK-121-01-01_Vision_Assistant_Result_Envelope_And_Status_Model.md) | Define the reusable result/report envelope for vision assistance |
| [TASK-121-01-02](./TASK-121-01-02_Vision_Policy_And_Truth_Boundary_Enforcement.md) | Enforce the boundary between vision assistance, router policy, and deterministic truth tools |

---

## Acceptance Criteria

- vision assistance has one stable contract and status vocabulary
- vision responsibilities do not blur into router policy or correctness truth
