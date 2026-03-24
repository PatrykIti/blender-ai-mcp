# TASK-113-05-03: Vision Boundaries and Lightweight Model Strategy

**Parent:** [TASK-113-05](./TASK-113-05_Vision_Measurement_And_Assertion_Layer.md)  
**Status:** ⏳ To Do  
**Priority:** 🟡 Medium

---

## Objective

Define how vision should help without taking over correctness responsibility.

---

## Exact Documentation Targets

- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/_MCP_SERVER/README.md`
- any future vision-workflow docs

---

## Required Rules

- vision may interpret, compare, and summarize
- vision may help localize issues
- vision should consume the active goal/session context
- vision should not be treated as the final source of geometric truth
- lightweight model guidance should be explicit:
  - when a lighter vision model is enough
  - when deterministic measure/assert should dominate

---

## Acceptance Criteria

- the repo has explicit guidance for when to use vision, and when not to trust it as final authority
