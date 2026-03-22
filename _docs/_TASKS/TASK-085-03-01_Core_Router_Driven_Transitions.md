# TASK-085-03-01: Core Router-Driven Phase Transitions

**Parent:** [TASK-085-03](./TASK-085-03_Router_Driven_Phase_Transitions.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-085-02](./TASK-085-02_Visibility_Policy_Engine_and_Tagged_Providers.md)

---

## Objective

Implement the core code changes for **Router-Driven Phase Transitions**.

---

## Repository Touchpoints

- `server/router/application/router.py`
- `server/application/tool_handlers/router_handler.py`
- `server/adapters/mcp/router_helper.py`

---

## Planned Work

- create `server/router/application/session_phase_hints.py`
- emit phase hints such as:
  - `planning` after `router_set_goal` resolves or requests clarification
  - `build` when workflow execution or expansion starts
  - `inspect_validate` when the guided surface hands off into inspection / validation flows
- let the FastMCP platform layer persist the final phase in session state

---

## Acceptance Criteria

- the router provides coarse phase hints only
- the visibility layer remains the owner of what becomes visible
- the first hint set uses the canonical subset names from TASK-085-01

---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep phase hints coarse and compatible with the first guided entry surface.
3. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
