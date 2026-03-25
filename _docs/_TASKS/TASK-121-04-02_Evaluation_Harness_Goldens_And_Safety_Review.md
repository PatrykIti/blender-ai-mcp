# TASK-121-04-02: Evaluation Harness, Goldens, and Safety Review

**Parent:** [TASK-121-04](./TASK-121-04_Lightweight_Vision_Runtime_And_Evaluation.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Add enough evaluation and governance for the vision-assist layer to be safely
iterated later.

---

## Implementation Direction

- build a small evaluation harness around representative scenarios:
  - visible improvement
  - visible regression
  - no meaningful change
  - mismatch against reference image
- keep goldens around:
  - capture bundles
  - expected likely-issue categories
  - expected recommended deterministic checks
- review safety/governance around:
  - false confidence
  - privacy of uploaded references
  - accidental use as truth source

---

## Repository Touchpoints

- `tests/unit/adapters/mcp/`
- `tests/e2e/`
- `_docs/_TESTS/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`

---

## Acceptance Criteria

- the vision layer has a real evaluation harness, not only qualitative demos
- governance risks are documented before broad rollout
