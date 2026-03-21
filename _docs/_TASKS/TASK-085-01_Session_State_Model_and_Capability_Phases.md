# TASK-085-01: Session State Model and Capability Phases

**Parent:** [TASK-085](./TASK-085_Session_Adaptive_Tool_Visibility.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-05](./TASK-083-05_Context_Session_and_Execution_Bridge.md)

---

## Objective

Define an explicit session state model and a deliberately small first-pass phase set that visibility rules can rely on.

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
  - optional read-only bootstrap metadata when useful for diagnostics

---

## Pseudocode

```python
class SessionPhase(StrEnum):
    BOOTSTRAP = "bootstrap"
    PLANNING = "planning"
    BUILD = "build"
    INSPECT = "inspect"
```

Optional future extensions such as `repair` or `export_handoff` should not block the first rollout.

### State Model Rule

Session state should keep runtime interaction state only.
It must not become a second bootstrap config system.

In particular:

- bootstrap config remains outside mutable session state
- `phase` changes during the session
- if profile/version metadata is stored for diagnostics, it should be read-only mirrored state, not a second config system

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-085-01-01](./TASK-085-01-01_Core_Session_State_Capability.md) | Core Session State Model and Capability Phases | Core implementation layer |
| [TASK-085-01-02](./TASK-085-01-02_Tests_Session_State_Capability.md) | Tests and Docs Session State Model and Capability Phases | Tests, docs, and QA |

---

## Acceptance Criteria

- phases are explicit, serializable, and not hidden inside private router fields
- the first phase model is intentionally coarse and small enough to operate reliably on the current sync-heavy repo

---

## Atomic Work Items

1. Define the minimal session-state schema and default values.
2. Add coarse phase helpers only for the first guided entry surface.
3. Add tests for persistence and reset behavior across turns.
4. Do not introduce fine-grained workflow phases until the coarse model proves useful.
