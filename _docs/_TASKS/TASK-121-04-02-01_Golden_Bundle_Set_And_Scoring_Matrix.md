# TASK-121-04-02-01: Golden Bundle Set and Scoring Matrix

**Parent:** [TASK-121-04-02](./TASK-121-04-02_Evaluation_Harness_Goldens_And_Safety_Review.md)  
**Status:** 🚧 In Progress  
**Priority:** 🔴 High

**Progress Update:** A first repo-tracked golden bundle set now exists under `tests/fixtures/vision_eval/`, together with scoring helpers that evaluate contract presence, direction/reference interpretation, capture usage, minimum completeness, and truth-claim safety. The current matrix is good enough for repeatable synthetic comparison; the next gap is expanding it to real macro capture bundles.

---

## Objective

Create one compact but representative set of capture/reference bundles and a
stable scoring matrix for backend comparison.

---

## Implementation Direction

- define a first golden bundle set covering:
  - synthetic smoke bundle
  - one `macro_finish_form` bundle
  - one `macro_relative_layout` bundle
  - one no-meaningful-change bundle
  - one reference mismatch bundle
- define one stable scoring matrix for:
  - JSON validity
  - contract completeness
  - issue usefulness
  - recommended-check usefulness
  - hallucinated truth claims
- keep the scoring matrix small enough to run often during runtime/prompt work

---

## Repository Touchpoints

- `tests/unit/adapters/mcp/`
- `scripts/`
- `_docs/_VISION/`
- `_docs/_TESTS/README.md`

---

## Acceptance Criteria

- backend comparison no longer depends on ad hoc manual judgment alone
- at least one first-pass golden bundle set exists and is reusable
