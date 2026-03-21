# TASK-092-03-01: Core Inspection Summarizer and Repair Suggester Assistants

**Parent:** [TASK-092-03](./TASK-092-03_Inspection_Summarizer_and_Repair_Suggester_Assistants.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-092-02](./TASK-092-02_Assistant_Runner_with_Typed_Result_Wrappers.md)

---

## Objective

Implement the core code changes for **Inspection Summarizer and Repair Suggester Assistants**.

---

## Repository Touchpoints

- `server/application/tool_handlers/scene_handler.py`
- `server/application/tool_handlers/mesh_handler.py`
- `server/router/application/router.py`

---

## Planned Work

### Deliverables

- implement the slice behavior end-to-end across: `server/application/tool_handlers/scene_handler.py`, `server/application/tool_handlers/mesh_handler.py`, `server/router/application/router.py`
- keep ownership boundaries explicit (FastMCP platform vs router policy vs inspection truth)
- preserve the parent task contract so this slice can be merged independently

### Implementation Checklist

- touch `server/application/tool_handlers/scene_handler.py` with an explicit change note (or explicit no-change rationale)
- touch `server/application/tool_handlers/mesh_handler.py` with an explicit change note (or explicit no-change rationale)
- touch `server/router/application/router.py` with an explicit change note (or explicit no-change rationale)
- add or update focused regression coverage for the changed slice behavior
- capture one before/after example of the affected runtime surface (payload, config, or execution flow)

### Review Notes To Attach

- short rationale for every changed touchpoint
- explicit note of any deferred work (if present) and why it is safe to defer
- exact test commands used for slice validation

---

## Acceptance Criteria

- every listed touchpoint is either updated or explicitly marked as no-change with justification
- the slice has at least one focused regression test proving intended behavior
- no boundary violations are introduced relative to `RESPONSIBILITY_BOUNDARIES.md`
- parent-level behavior remains compatible when this slice lands alone

---

## Atomic Work Items

1. Implement the scoped behavior in the listed touchpoints with explicit boundary ownership.
2. Add/adjust regression tests for the changed behavior and verify deterministic outcomes.
3. Record before/after evidence for the changed surface (contract, visibility, routing, or runtime behavior).
4. Document any deferred edges and why they do not block parent-task acceptance.
