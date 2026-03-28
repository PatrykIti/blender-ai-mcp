# 160 - 2026-03-28: Real viewport vision view variants

**Status**: ✅ Completed  
**Type**: Evaluation / Vision Harness  
**Task**: TASK-121-04

---

## Summary

Added repo-tracked real viewport vision scenarios for two additional view
families on the squirrel progression set:

- direct top `USER_PERSPECTIVE` captures
- fixed named-camera perspective captures

Ran both local MLX baselines against those new scenarios.

Short result:

- `Qwen3-VL-2B-Instruct-4bit`: `strong` on all 6 new scenarios, `1.0` on all
  6, but materially noisier (`11` likely issues + `6` recommended checks)
- `Qwen3-VL-4B-Instruct-4bit`: `strong` on all 6 new scenarios, cleaner output
  with `0` likely issues and `0` recommended checks, but `0.875` on 2/6 due to
  current scoring-heuristic phrasing sensitivity

---

## Changes

- Added 6 new golden/bundle fixture families under `tests/fixtures/vision_eval/`
- Added regression coverage for loading and scoring those new scenarios
- Added an opt-in real-model comparison test for `2B` vs `4B`
- Updated vision/test docs and the root README with a short note about the new
  eval coverage and comparison outcome

---

## Validation

- `poetry run pytest -q tests/unit/adapters/mcp/test_vision_evaluation.py tests/unit/adapters/mcp/test_vision_capture_bundle.py`
- `poetry run pytest tests/unit/adapters/mcp/test_vision_evaluation.py -k 'user_top or camera_perspective' -vv`
- local `mlx_local` harness runs against all 6 new scenarios for:
  - `mlx-community/Qwen3-VL-2B-Instruct-4bit`
  - `mlx-community/Qwen3-VL-4B-Instruct-4bit`
