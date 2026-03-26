# TASK-121-03-02: Macro/Workflow Vision Integration Path

**Parent:** [TASK-121-03](./TASK-121-03_Before_After_Capture_And_Macro_Integration.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Integrate vision assistance into macro/workflow paths rather than exposing it as
an isolated free-floating tool first.

---

## Implementation Direction

- attach vision assistance to bounded macro/workflow reports using:
  - active goal
  - reference images
  - capture bundles
  - optional inspect/measure/assert summaries
- do not call vision first on arbitrary viewport images; integrate it after deterministic capture-bundle creation
- vision output should recommend deterministic next checks where needed
- keep request-bound execution; do not turn vision into a background authority

---

## Repository Touchpoints

- macro/report contracts from `TASK-120`
- `server/adapters/mcp/sampling/`
- `server/adapters/mcp/contracts/`
- `tests/unit/adapters/mcp/`
- `tests/e2e/`

---

## Acceptance Criteria

- macro/workflow reports can carry bounded visual interpretation
- deterministic follow-up checks remain the preferred way to confirm correctness
- macro/workflow integrations use stable before/after comparisons rather than one-shot image guessing
