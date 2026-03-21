# TASK-097-03: Postcondition Registry for High-Risk Fixes

**Parent:** [TASK-097](./TASK-097_Transparent_Correction_Audit_and_Postconditions.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-097-01](./TASK-097-01_Correction_Event_Model_and_Audit_Schema.md)

---

## Objective

Register which correction classes require postcondition verification after execution.

---

## Planned Work

- create:
  - `server/router/domain/entities/postcondition.py`
  - `server/router/application/policy/postcondition_registry.py`

---

## Acceptance Criteria

- the repo knows which fixes require post-execution verification
