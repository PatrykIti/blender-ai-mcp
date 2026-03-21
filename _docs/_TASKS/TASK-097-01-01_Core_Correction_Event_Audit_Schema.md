# TASK-097-01-01: Core Correction Event Model and Audit Schema

**Parent:** [TASK-097-01](./TASK-097-01_Correction_Event_Model_and_Audit_Schema.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-097-01](./TASK-097-01_Correction_Event_Model_and_Audit_Schema.md)  

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
- `tests/unit/router/application/test_correction_audit.py`

---

## Planned Work

- Implement the primary code changes described in the parent task.
- Keep responsibilities aligned with Clean Architecture and `RESPONSIBILITY_BOUNDARIES.md`.
- Avoid introducing new bootstrap side effects outside the platform composition root.

---

## Acceptance Criteria

- Core implementation is complete and aligned with the parent scope.

---

## Atomic Work Items

1. Define a structured correction audit entity that separates correction intent, decision basis, execution steps, and verification outcome.
2. Make router execution reporting reference audit events instead of relying on concatenated text or log-only explanations.
3. Keep audit payloads serializable and machine-readable so adapters can render them as structured output or summary text without changing the source data model.
