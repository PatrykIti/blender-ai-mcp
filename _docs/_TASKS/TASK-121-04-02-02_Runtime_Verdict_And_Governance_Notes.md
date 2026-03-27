# TASK-121-04-02-02: Runtime Verdict and Governance Notes

**Parent:** [TASK-121-04-02](./TASK-121-04-02_Evaluation_Harness_Goldens_And_Safety_Review.md)  
**Status:** 🚧 In Progress  
**Priority:** 🔴 High

**Progress Update:** The repo now has an initial scored baseline for `mlx_local` on both synthetic scenarios and several real viewport scenarios. `Qwen3-VL-4B-Instruct-4bit` now scores a clean `1.0` on the real cube-to-picnic-table smoke case and on the squirrel progression cases. `Qwen3-VL-2B-Instruct-4bit` also reaches `1.0` on the squirrel progression cases, but it remains noisier and still lands lower (`0.875`) on the cube-to-picnic-table smoke case because of weaker/noisier phrasing and extra issue/check output. Current governance interpretation remains the same: `4B` is the cleaner practical local baseline, while `2B` is viable for smoke/dev and some progression cases but still noisier.

---

## Objective

Turn raw smoke/eval findings into one explicit verdict about which backend
paths are useful, experimental, or not yet ready.

---

## Implementation Direction

- classify backend/model combinations into:
  - smoke-test-only
  - usable for local experimentation
  - candidate for guarded product use
- record known weaknesses such as:
  - input echo tendency
  - empty but valid contract outputs
  - weak issue localization
  - weak deterministic-check recommendation quality
- keep governance notes explicit around:
  - false confidence
  - misleading "valid JSON but useless semantics"
  - privacy of reference images

---

## Repository Touchpoints

- `_docs/_VISION/`
- `_docs/_TASKS/`
- `_docs/_TESTS/README.md`

---

## Acceptance Criteria

- the repo has one explicit verdict for current backend paths
- later model work can be evaluated against a recorded baseline instead of memory
