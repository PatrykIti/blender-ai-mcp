# TASK-089-02-01: Core Structured Scene Context and Inspection Contracts

**Parent:** [TASK-089-02](./TASK-089-02_Structured_Scene_Context_and_Inspection_Contracts.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-089-02](./TASK-089-02_Structured_Scene_Context_and_Inspection_Contracts.md)  

---

## Objective

Implement the core code changes for **Structured Scene Context and Inspection Contracts**.

---

## Repository Touchpoints

- `server/application/tool_handlers/scene_handler.py`
- `server/adapters/mcp/areas/scene.py`
- `server/domain/tools/scene.py`

---

## Planned Work

- Implement the primary code changes described in the parent task.
- Keep responsibilities aligned with Clean Architecture and `RESPONSIBILITY_BOUNDARIES.md`.
- Avoid introducing new bootstrap side effects outside the platform composition root.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-089-02-01-01](./TASK-089-02-01-01_Scene_Contract_Definitions.md) | Scene Contract Definitions | Core slice |
| [TASK-089-02-01-02](./TASK-089-02-01-02_Handler_and_Adapter_Integration.md) | Handler and Adapter Integration | Core slice |

---

## Acceptance Criteria

- Core implementation is complete and aligned with the parent scope.

---

## Atomic Work Items

1. Apply the core changes in the relevant adapters/handlers.
2. Verify the core flow still matches the expected execution path.
