# TASK-092-04-01: Core Router Integration, Masking, and Budget Control

**Parent:** [TASK-092-04](./TASK-092-04_Router_Integration_Masking_and_Budget_Control.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-092-03](./TASK-092-03_Inspection_Summarizer_and_Repair_Suggester_Assistants.md)

---

## Objective

Implement the core code changes for **Router Integration, Masking, and Budget Control**.

---

## Repository Touchpoints

- `server/adapters/mcp/sampling/assistant_runner.py`
- `server/router/application/router.py`
- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/contracts/router.py`
- `tests/unit/router/application/test_correction_policy_engine.py`
---

## Planned Work

- Implement the concrete leaf scope implied by the parent task in the listed touchpoints.
- Keep responsibilities aligned with Clean Architecture and `RESPONSIBILITY_BOUNDARIES.md`.
- Avoid introducing new bootstrap side effects outside the platform composition root.

---

## Acceptance Criteria

- assistants are bounded and cannot expand into free-form agent sprawl
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
