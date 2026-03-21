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
  - `pending_clarification`
  - `last_router_status`
  - optional read-only bootstrap metadata for diagnostics only

---

## Acceptance Criteria

- phases are explicit, serializable, and not hidden inside private router fields
- the first implementation uses a coarse phase model only

---

## Atomic Work Items

1. Define the minimal session-state schema and default values.
2. Add coarse phase helpers for the first guided entry surface only.
3. Keep bootstrap profile/version config outside mutable session state.
4. Add tests for persistence and reset behavior across turns.
