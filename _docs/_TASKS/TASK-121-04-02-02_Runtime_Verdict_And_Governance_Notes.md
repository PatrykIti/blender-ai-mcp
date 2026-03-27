# TASK-121-04-02-02: Runtime Verdict and Governance Notes

**Parent:** [TASK-121-04-02](./TASK-121-04-02_Evaluation_Harness_Goldens_And_Safety_Review.md)  
**Status:** 🚧 In Progress  
**Priority:** 🔴 High

**Progress Update:** The repo now has an initial scored baseline for `mlx_local` on both synthetic scenarios and one first real viewport smoke scenario (`default_cube_to_picnic_table`). Current recorded interpretation: both `Qwen3-VL-2B-Instruct-4bit` and `Qwen3-VL-4B-Instruct-4bit` can look strong on narrow synthetic bundles, and both can correctly describe a large scene replacement smoke case. After the latest heuristic update, `4B` now scores a clean `1.0` on that real smoke case, while `2B` still lands lower because it is noisier and uses wording that does not always map cleanly through the direction heuristic. The next step is to record verdicts on harder scenarios, especially real macro bundles and mismatch cases.

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
