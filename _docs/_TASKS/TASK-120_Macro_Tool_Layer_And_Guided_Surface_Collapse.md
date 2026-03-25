# TASK-120: Macro Tool Layer and Guided Surface Collapse

**Priority:** 🔴 High  
**Category:** Product Surface Expansion / Macro Layer  
**Estimated Effort:** Large  
**Dependencies:** TASK-113, TASK-114, TASK-119  
**Status:** 🚧 In Progress

**Progress Update:** The first macro-design slice is now in place and the first two bounded macro tools exist in code/tests/docs: candidate selection has been grounded in existing workflows, the shared machine-readable macro report envelope exists in code/tests, `macro_cutout_recess` has Blender-backed regression coverage, and `macro_relative_layout` now covers bounded part placement/layout over existing scene/modeling tools. The next step is `macro_finish_form`, then using the broader macro layer to collapse the guided surface further.

---

## Objective

Introduce a bounded macro-tool layer so `llm-guided` can expose more modeling
power while hiding more of the low-level atomic surface.

---

## Business Problem

The current grouped/public layer is better than the historical flat catalog, but
it still leaves a gap:

- atomics are too low-level for many normal LLM tasks
- full workflows are too heavy for many mid-complexity editing intents
- the guided surface cannot hide much more until a stronger mid-layer exists

Without a macro layer, the repo either exposes too many atomics or pushes too
many tasks into heavyweight workflow paths.

---

## Business Outcome

If this wave is done correctly, the repo gains:

- a bounded macro layer between grouped tools and full workflows
- more room to shrink the public guided surface
- fewer wrong low-level tool choices by LLMs
- cleaner integration points for later vision-assisted reporting

---

## Scope

This umbrella covers:

- macro candidate selection and shared report contracts
- the first bounded macro family
- guided-surface collapse once macro tools exist
- rollout validation, benchmarking, and prompt/instruction integration

This umbrella does **not** create an unbounded “do anything” macro tool.
It creates a small bounded macro layer with explicit ownership.

---

## Success Criteria

- the repo has a first bounded macro layer above atomics and below workflows
- `llm-guided` can hide more atomics without reducing useful modeling power
- macro results are structured enough to support later vision and verification layers

---

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-120-01](./TASK-120-01_Macro_Candidate_Matrix_And_Shared_Contract.md) | Choose first macro families and define one shared macro report contract |
| 2 | [TASK-120-02](./TASK-120-02_First_Macro_Wave_Form_Cutout_And_Layout.md) | Implement the first bounded macro wave for hard-surface modeling tasks |
| 3 | [TASK-120-03](./TASK-120-03_Guided_Surface_Collapse_And_Discovery_Preference.md) | Collapse the guided surface and bias discovery toward macro tools |
| 4 | [TASK-120-04](./TASK-120-04_Macro_Validation_And_Adoption.md) | Protect and operationalize the macro layer through tests, prompts, and rollout docs |
