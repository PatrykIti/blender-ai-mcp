# TASK-121-02-01: Goal-Scoped Reference Context in Session State

**Parent:** [TASK-121-02](./TASK-121-02_Goal_And_Reference_Context_Session_Model.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Persist reference-image context as part of the active goal/session state.

---

## Implementation Direction

- extend session state with fields such as:
  - active goal id/text
  - reference image ids
  - style/acceptance notes
  - optional target-object or target-view hints
- bind reference context to `router_set_goal(...)` lifecycle instead of creating
  a parallel unrelated state model
- keep it lightweight and session-scoped first

---

## Repository Touchpoints

- `server/adapters/mcp/session_state.py`
- `server/adapters/mcp/areas/router.py`
- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/unit/adapters/mcp/`

---

## Acceptance Criteria

- reference context follows the active goal instead of floating separately
- later vision/capture tools can consume one stable goal-scoped context source
