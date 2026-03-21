# TASK-097-01: Correction Event Model and Audit Schema

**Parent:** [TASK-097](./TASK-097_Transparent_Correction_Audit_and_Postconditions.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-089-04](./TASK-089-04_Router_Workflow_and_Execution_Report_Contracts.md), [TASK-096-03](./TASK-096-03_Auto_Fix_Ask_Block_Policy_Engine.md)

---

## Objective

Define the event model and schema for correction audit trails.

---

## Planned Work

- create:
  - `server/router/domain/entities/correction_audit.py`
  - `server/adapters/mcp/contracts/correction_audit.py`
- wire new runtime audit collaborators through `server/infrastructure/di.py` when introduced

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-097-01-01](./TASK-097-01-01_Core_Correction_Event_Audit_Schema.md) | Core Correction Event Model and Audit Schema | Core implementation layer |
| [TASK-097-01-02](./TASK-097-01-02_Tests_Correction_Event_Audit_Schema.md) | Tests and Docs Correction Event Model and Audit Schema | Tests, docs, and QA |

---

## Acceptance Criteria

- correction intent, execution, and verification have separate fields in the audit model
