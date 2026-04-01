# TASK-121-05-04: Guided Discovery Tool Persistence Across Session Visibility

**Parent:** [TASK-121-05](./TASK-121-05_Guided_Utility_Capture_Prep_And_Goal_Boundary.md)  
**Status:** 🚧 In Progress  
**Priority:** 🔴 High

**Progress Update:** The guided visibility rules now carry an explicit discovery-tool set for `search_tools` and `call_tool`, and session visibility reapplication no longer drops the guided surface from `8` tools to `6` after the first goal/workflow transition. Remaining work is mostly higher-level runtime validation against real reconnect/client behavior.

---

## Objective

Ensure `search_tools` and `call_tool` remain available across guided session
phase/visibility updates instead of disappearing after the first workflow or
goal-state transition.

---

## Business Problem

On a fresh guided session, the client sees the expected `8` entry tools. After
`router_set_goal(...)` or other stateful actions, the session visibility rules
are reapplied and `search_tools` / `call_tool` can disappear, dropping the
surface to `6` tools.

That breaks the core search-first public interaction model and makes guided
sessions inconsistent:

- the product instructions still mention discovery tools
- the client saw them at session start
- but the server hides them after the first meaningful interaction

---

## Implementation Direction

- define an explicit guided discovery tool set:
  - `search_tools`
  - `call_tool`
- keep that set enabled across guided phases whenever session visibility is
  reapplied
- make the rules deterministic and owned by FastMCP visibility policy, not by
  ad hoc client behavior
- add regression coverage for:
  - session visibility application
  - guided mode diagnostics
  - search-first bootstrap/build behavior

---

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/guided_mode.py`
- `server/adapters/mcp/session_capabilities.py`
- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`

---

## Acceptance Criteria

- `search_tools` and `call_tool` do not disappear after guided session updates
- guided bootstrap/build/inspect visibility stays coherent with product docs
- session visibility updates no longer reduce the guided surface from `8` to `6`
