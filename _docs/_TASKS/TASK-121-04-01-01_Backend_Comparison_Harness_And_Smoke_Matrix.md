# TASK-121-04-01-01: Backend Comparison Harness and Smoke Matrix

**Parent:** [TASK-121-04-01](./TASK-121-04-01_Small_Vision_Runtime_Selection_And_Execution_Policy.md)  
**Status:** 🚧 In Progress  
**Priority:** 🔴 High

**Progress Update:** `scripts/vision_harness.py` now exists and can run the same bundle/reference payload through at least `mlx_local` and other configured backends. It now also supports repo-tracked `golden.json` scenarios and emits scored evaluation summaries. Preliminary MLX comparison shows that both `Qwen3-VL-2B-Instruct-4bit` and `Qwen3-VL-4B-Instruct-4bit` can score well on the first synthetic scenarios, but harder scenario coverage is still needed before making a product-facing local-model verdict.

---

## Objective

Create one repeatable harness for comparing local and external vision backends
against the same bounded inputs.

---

## Implementation Direction

- keep one script entrypoint for:
  - bundle JSON + references JSON
  - explicit backend selection
  - raw and parsed output capture
- ensure the harness can compare:
  - `mlx_local`
  - `transformers_local`
  - `openai_compatible_external`
- record smoke-matrix outcomes such as:
  - runtime boot success/failure
  - model load success/failure
  - parse success/failure
  - raw output shape class (`json`, fenced json, prose, input echo)
  - qualitative verdict (`smoke/dev only`, `real local trial candidate`, `reject`)

---

## Repository Touchpoints

- `scripts/vision_harness.py`
- `tests/unit/scripts/`
- `_docs/_VISION/`

---

## Acceptance Criteria

- one harness can exercise multiple backend families on the same input
- smoke results can be compared without manual one-off shell experimentation
