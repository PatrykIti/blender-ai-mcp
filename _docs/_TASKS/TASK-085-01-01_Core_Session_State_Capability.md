# TASK-085-01-01: Core Session State Model and Capability Phases

**Parent:** [TASK-085-01](./TASK-085-01_Session_State_Model_and_Capability_Phases.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-05](./TASK-083-05_Context_Session_and_Execution_Bridge.md)

---

## Objective

Implement the core code changes for **Session State Model and Capability Phases**.

---

## Repository Touchpoints

- `server/router/application/router.py`
- `server/application/tool_handlers/router_handler.py`
- `server/adapters/mcp/context_utils.py`

---

## Planned Work

- create:
  - `server/adapters/mcp/session_phase.py`
  - `server/adapters/mcp/session_capabilities.py`
  - `tests/unit/adapters/mcp/test_session_phase.py`
- store in session state:
  - `phase`
  - `goal`
  - `active_surface_profile`
  - `active_contract_line`
  - `last_router_status`
---

## Acceptance Criteria

- phases are explicit, serializable, and not hidden inside private router fields
---

## Atomic Work Items

1. Define the session-state schema and default values.
2. Add profile, contract-line, and phase helpers.
3. Add tests for persistence and reset behavior across turns.