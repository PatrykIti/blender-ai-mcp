# TASK-094-02-01: Core Read-Only Code Mode Pilot Surface

**Parent:** [TASK-094-02](./TASK-094-02_Read_Only_Code_Mode_Pilot_Surface.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-094-01](./TASK-094-01_Code_Mode_Experiment_Design_and_Guardrails.md)

---

## Objective

Implement the core code changes for **Read-Only Code Mode Pilot Surface**.

---

## Repository Touchpoints

- `server/application/tool_handlers/scene_handler.py`
- `server/application/tool_handlers/mesh_handler.py`
- `server/application/tool_handlers/workflow_catalog_handler.py`

---

## Planned Work

### Slice Outputs

- deliver explicit experimental Code Mode behavior with guardrails
- limit pilot surface to approved read-heavy workflows
- produce measurable comparison artifacts against classic tool loops

### Implementation Checklist

- touch `server/application/tool_handlers/scene_handler.py` with explicit change notes and boundary rationale
- touch `server/application/tool_handlers/mesh_handler.py` with explicit change notes and boundary rationale
- touch `server/application/tool_handlers/workflow_catalog_handler.py` with explicit change notes and boundary rationale
- add or update focused regression coverage for the slice behavior
- capture before/after evidence tied to the slice outputs

### Review Notes To Attach

- rationale per changed touchpoint and any explicit no-change decisions
- exact test commands and profile/config context used during validation
- deferred work list with safety rationale

---

## Acceptance Criteria

- code-mode experiment boundaries are explicit and enforceable
- write/destructive operations are blocked where required
- benchmark artifacts are reproducible and linked to recommendations
- slice remains profile-scoped and opt-in only

---

## Atomic Work Items

1. Implement pilot/benchmark/documentation behavior in listed touchpoints.
2. Add tests for guardrail enforcement and discovery/execution flow.
3. Capture benchmark metrics vs classic tool-loop baseline.
4. Document go/no-go criteria and retained constraints.
