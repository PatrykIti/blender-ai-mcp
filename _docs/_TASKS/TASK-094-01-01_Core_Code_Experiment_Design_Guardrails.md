# TASK-094-01-01: Core Code Mode Experiment Design and Guardrails

**Parent:** [TASK-094-01](./TASK-094-01_Code_Mode_Experiment_Design_and_Guardrails.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-083-04](./TASK-083-04_Transform_Pipeline_Baseline.md), [TASK-084-02](./TASK-084-02_Search_Transform_and_Pinned_Entry_Surface.md)

---

## Objective

Implement the core code changes for **Code Mode Experiment Design and Guardrails**.

---

## Repository Touchpoints

- `server/adapters/mcp/surfaces.py`
- `server/adapters/mcp/settings.py`
- `tests/unit/adapters/mcp/test_server_factory.py`
- `_docs/_MCP_SERVER/README.md`
---

## Planned Work

- Implement the concrete leaf scope implied by the parent task in the listed touchpoints.
- Keep responsibilities aligned with Clean Architecture and `RESPONSIBILITY_BOUNDARIES.md`.
- Avoid introducing new bootstrap side effects outside the platform composition root.

---

## Acceptance Criteria

- Code Mode is explicitly scoped as experimental
- write-heavy or destructive Blender operations are excluded from the default experiment
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
