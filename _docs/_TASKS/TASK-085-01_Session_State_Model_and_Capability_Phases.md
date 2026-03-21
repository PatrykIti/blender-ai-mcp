# TASK-085-01: Session State Model and Capability Phases

**Parent:** [TASK-085](./TASK-085_Session_Adaptive_Tool_Visibility.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-05](./TASK-083-05_Context_Session_and_Execution_Bridge.md)

---

## Objective

Define an explicit session state model and a small set of capability phases that visibility rules can rely on.

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

## Pseudocode

```python
class SessionPhase(StrEnum):
    BOOTSTRAP = "bootstrap"
    PLANNING = "planning"
    WORKFLOW_RESOLUTION = "workflow_resolution"
    BUILD = "build"
    INSPECT_VALIDATE = "inspect_validate"
    REPAIR = "repair"
    EXPORT_HANDOFF = "export_handoff"
```

### State Model Rule

Session state should keep runtime interaction state only.
It must not become a second bootstrap config system.

In particular:

- `active_surface_profile` comes from bootstrap
- `active_contract_line` comes from version selection
- `phase` changes during the session

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-085-01-01](./TASK-085-01-01_Core_Session_State_Capability.md) | Core Session State Model and Capability Phases | Core implementation layer |
| [TASK-085-01-02](./TASK-085-01-02_Tests_Session_State_Capability.md) | Tests and Docs Session State Model and Capability Phases | Tests, docs, and QA |

---

## Acceptance Criteria

- phases are explicit, serializable, and not hidden inside private router fields

---

## Atomic Work Items

1. Define the session-state schema and default values.
2. Add profile, contract-line, and phase helpers.
3. Add tests for persistence and reset behavior across turns.
