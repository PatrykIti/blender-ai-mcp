# TASK-120-04-01: Macro Regression and Benchmark Pack

**Parent:** [TASK-120-04](./TASK-120-04_Macro_Validation_And_Adoption.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** The first macro wave is now protected by a focused regression/benchmark pack: shared macro contracts and structured delivery are covered in unit tests, guided-surface benchmark baselines assert payload/tool-count behavior plus reduced finishing decision points on `llm-guided`, and Blender-backed E2E regressions now exist for `macro_cutout_recess`, `macro_finish_form`, and `macro_relative_layout`.

---

## Objective

Create a focused regression/benchmark suite for the first macro wave.

---

## Implementation Direction

- cover:
  - macro contract shape
  - macro result semantics
  - guided visibility impact
  - tool-count and payload-size baselines
  - representative E2E macro flows
- benchmark whether macro introduction reduces low-level decision count on the guided surface

---

## Repository Touchpoints

- `tests/unit/adapters/mcp/`
- `tests/unit/tools/`
- `tests/e2e/tools/`
- `_docs/_TESTS/README.md`

---

## Acceptance Criteria

- macro-wave regression coverage exists before further guided-surface collapse
- benchmark baselines show whether the macro wave improves the public model
