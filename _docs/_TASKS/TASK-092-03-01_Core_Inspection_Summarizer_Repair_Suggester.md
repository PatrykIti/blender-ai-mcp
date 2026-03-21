# TASK-092-03-01: Core Inspection Summarizer and Repair Suggester Assistants

**Parent:** [TASK-092-03](./TASK-092-03_Inspection_Summarizer_and_Repair_Suggester_Assistants.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-092-02](./TASK-092-02_Assistant_Runner_with_Typed_Result_Wrappers.md)

---

## Objective

Implement the core code changes for **Inspection Summarizer and Repair Suggester Assistants**.

---

## Repository Touchpoints

- `server/application/tool_handlers/scene_handler.py`
- `server/application/tool_handlers/mesh_handler.py`
- `server/router/application/router.py`

---

## Planned Work

- Implement the concrete leaf scope implied by the parent task in the listed touchpoints.
- Keep responsibilities aligned with Clean Architecture and `RESPONSIBILITY_BOUNDARIES.md`.
- Avoid introducing new bootstrap side effects outside the platform composition root.

---

## Acceptance Criteria

- at least one assistant can digest large inspection payloads into a structured summary
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
