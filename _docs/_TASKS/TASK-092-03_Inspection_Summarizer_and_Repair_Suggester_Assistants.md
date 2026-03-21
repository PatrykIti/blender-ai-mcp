# TASK-092-03: Inspection Summarizer and Repair Suggester Assistants

**Parent:** [TASK-092](./TASK-092_Server_Side_Sampling_Assistants.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-092-02](./TASK-092-02_Assistant_Runner_with_Typed_Result_Wrappers.md)

---

## Objective

Ship the first two bounded analytical assistants:

- an inspection summarizer
- a repair suggester

---

## Repository Touchpoints

- `server/application/tool_handlers/scene_handler.py`
- `server/application/tool_handlers/mesh_handler.py`
- `server/router/application/router.py`

---

## Acceptance Criteria

- at least one assistant can digest large inspection payloads into a structured summary
