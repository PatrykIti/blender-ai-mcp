# TASK-097-01-01: Core Correction Event Model and Audit Schema

**Parent:** [TASK-097-01](./TASK-097-01_Correction_Event_Model_and_Audit_Schema.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-089-04](./TASK-089-04_Router_Workflow_and_Execution_Report_Contracts.md), [TASK-096-03](./TASK-096-03_Auto_Fix_Ask_Block_Policy_Engine.md)

---

## Objective

Implement the core code changes for **Correction Event Model and Audit Schema**.

---

## Repository Touchpoints

- `server/router/domain/entities/correction_audit.py`
- `server/adapters/mcp/contracts/correction_audit.py`
- `server/adapters/mcp/execution_report.py`
- `server/adapters/mcp/router_helper.py`
- `server/router/application/router.py`
- `server/router/infrastructure/logger.py`
- `server/infrastructure/di.py`
- `tests/unit/router/application/test_correction_audit.py`

---

## Planned Work

- create:
  - `server/router/domain/entities/correction_audit.py`
  - `server/adapters/mcp/contracts/correction_audit.py`
- wire runtime audit collaborators via `server/infrastructure/di.py` when new services/providers are introduced
---

## Acceptance Criteria

- correction intent, execution, and verification have separate fields in the audit model
- runtime audit collaborators are wired through DI without hidden adapter-level construction
---

## Atomic Work Items

1. Define a structured correction audit entity that separates correction intent, decision basis, execution steps, and verification outcome.
2. Make router execution reporting reference audit events instead of relying on concatenated text or log-only explanations.
3. Keep audit payloads serializable and machine-readable so adapters can render them as structured output or summary text without changing the source data model.
