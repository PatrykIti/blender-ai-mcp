# 162 - 2026-03-29: Vision local output and scoring tuning

**Status**: ✅ Completed  
**Type**: Vision Runtime / Evaluation  
**Task**: TASK-121-04

---

## Summary

Tightened the local vision output path and the easy-scenario scoring rules:

- local prompts now push harder for concrete `visible_changes`
- local prompts now explicitly discourage filler `likely_issues` /
  `recommended_checks`
- parse repair now deduplicates repeated issue/check output
- easy smoke/progression scenarios can now penalize extra issue/check noise
- direction heuristics now better recognize concise 4B progression wording on
  the real squirrel view-family variants

---

## Validation

- `poetry run pytest -q tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_parsing.py tests/unit/adapters/mcp/test_vision_evaluation.py tests/unit/adapters/mcp/test_vision_local_backend.py`
- local MLX rerun confirmed the two previously under-scored 4B cases now score
  `1.0` / `strong`
