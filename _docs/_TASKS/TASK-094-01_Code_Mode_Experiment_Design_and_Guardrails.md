# TASK-094-01: Code Mode Experiment Design and Guardrails

**Parent:** [TASK-094](./TASK-094_Code_Mode_Exploration.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-083-04](./TASK-083-04_Transform_Pipeline_Baseline.md)

---

## Objective

Define the Code Mode experiment scope, success criteria, and hard guardrails before any pilot surface is exposed.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-094-01-01](./TASK-094-01-01_Core_Code_Experiment_Design_Guardrails.md) | Core Code Mode Experiment Design and Guardrails | Core implementation layer |
| [TASK-094-01-02](./TASK-094-01-02_Tests_Code_Experiment_Design_Guardrails.md) | Tests and Docs Code Mode Experiment Design and Guardrails | Tests, docs, and QA |

---

## Acceptance Criteria

- Code Mode is explicitly scoped as experimental
- write-heavy or destructive Blender operations are excluded from the default experiment
- the experiment explicitly forbids raw Python / `bpy` execution and uses only the composed MCP surface as its orchestration substrate
