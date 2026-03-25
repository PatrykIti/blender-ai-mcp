# TASK-121-02: Goal and Reference Context Session Model

**Parent:** [TASK-121](./TASK-121_Goal_Aware_Vision_Assist_And_Reference_Context.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Add goal-scoped reference-image context to session state so macro/workflow paths
can interpret visual changes against the active build goal.

---

## Repository Touchpoints

- `server/adapters/mcp/session_state.py`
- `server/adapters/mcp/session_phase.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/areas/`
- `server/infrastructure/tmp_paths.py`
- `tests/unit/adapters/mcp/`

---

## Leaf Breakdown

| Leaf | Purpose |
|------|---------|
| [TASK-121-02-01](./TASK-121-02-01_Goal_Scoped_Reference_Context_In_Session_State.md) | Extend session state with goal-bound reference-image metadata and interpretation hints |
| [TASK-121-02-02](./TASK-121-02-02_Reference_Image_Intake_And_Lifecycle_API.md) | Add upload/intake/list/remove lifecycle APIs for session-scoped reference images |

---

## Acceptance Criteria

- active goals can carry reference-image context inside the MCP session model
- reference-image lifecycle is explicit and bounded before persistent asset management is considered
