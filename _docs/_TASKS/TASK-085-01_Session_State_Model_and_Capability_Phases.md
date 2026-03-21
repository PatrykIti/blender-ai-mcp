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

---

## Acceptance Criteria

- phases are explicit, serializable, and not hidden inside private router fields
