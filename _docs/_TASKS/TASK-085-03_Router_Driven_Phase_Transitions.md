# TASK-085-03: Router-Driven Phase Transitions

**Parent:** [TASK-085](./TASK-085_Session_Adaptive_Tool_Visibility.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-085-02](./TASK-085-02_Visibility_Policy_Engine_and_Tagged_Providers.md)

---

## Objective

Feed router state changes into session phase transitions without moving discovery or visibility ownership into the router.

---

## Repository Touchpoints

- `server/router/application/router.py`
- `server/application/tool_handlers/router_handler.py`
- `server/adapters/mcp/router_helper.py`

---

## Planned Work

- create `server/router/application/session_phase_hints.py`
- emit phase hints such as:
  - `workflow_resolution` after `router_set_goal`
  - `build` when workflow execution or expansion starts
  - `repair` after firewall blocks or high-risk correction paths
- let the FastMCP platform layer persist the final phase in session state

---

## Pseudocode

```python
if router_result.pending_workflow:
    phase_hint = "workflow_resolution"
elif router_result.executed_workflow:
    phase_hint = "build"
elif router_result.blocked_calls > 0:
    phase_hint = "repair"
```

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-085-03-01](./TASK-085-03-01_Core_Router_Driven_Transitions.md) | Core Router-Driven Phase Transitions | Core implementation layer |
| [TASK-085-03-02](./TASK-085-03-02_Tests_Router_Driven_Transitions.md) | Tests and Docs Router-Driven Phase Transitions | Tests, docs, and QA |

---

## Acceptance Criteria

- the router provides phase hints only
- the visibility layer remains the owner of what becomes visible
