# TASK-096-05-01: Core Session Memory and Operator Transparency

**Parent:** [TASK-096-05](./TASK-096-05_Session_Memory_and_Operator_Transparency.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-085-01](./TASK-085-01_Session_State_Model_and_Capability_Phases.md), [TASK-096-03](./TASK-096-03_Auto_Fix_Ask_Block_Policy_Engine.md)

---

## Objective

Implement the core code changes for **Session Memory and Operator Transparency**.

---

## Repository Touchpoints

- `server/adapters/mcp/session_state.py`
- `server/adapters/mcp/execution_report.py`
- `server/adapters/mcp/areas/router.py`
- `server/application/tool_handlers/router_handler.py`
- `server/adapters/mcp/contracts/router.py`
---

## Planned Work

- Implement the concrete leaf scope implied by the parent task in the listed touchpoints.
- Keep responsibilities aligned with Clean Architecture and `RESPONSIBILITY_BOUNDARIES.md`.
- Avoid introducing new bootstrap side effects outside the platform composition root.

---

## Acceptance Criteria

- confidence decisions are visible in status or debug payloads
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
