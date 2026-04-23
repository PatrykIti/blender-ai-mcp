# 254. Guided stage checkpoint, viewport, and silhouette fixes

Date: 2026-04-23

## Summary

Fixed three guided reference-loop correctness gaps:

- incomplete guided build stages no longer advance just because
  `reference_iterate_stage_checkpoint(...)` returns
  `loop_disposition="continue_build"`
- persisted current-view compares no longer apply the same user-view
  adjustments twice while building compact view-diagnostics hints
- deterministic silhouette analysis now uses the matching target/focus capture
  when available instead of defaulting to the broad context capture

## What Changed

- in `server/adapters/mcp/session_capabilities.py`:
  - held `create_primary_masses` and `place_secondary_parts` in place when the
    current role summary still has missing required roles
  - kept the role summary and optional spatial refresh gate coherent without
    marking the unfinished step as completed
- in `server/adapters/mcp/areas/reference.py`:
  - selected silhouette captures by matching `target_view` and `view_kind`
    before falling back to `context_wide`
  - neutralized diagnostics-only `focus_target`, `view_name`, orbit, and zoom
    arguments after a persisted current-view capture has already applied them
- in `tests/unit/adapters/mcp/test_reference_images.py`:
  - added regressions for incomplete-stage holds, persisted-view diagnostics,
    and focus-capture silhouette selection
- updated public/operator docs in:
  - `README.md`
  - `_docs/_MCP_SERVER/README.md`
  - `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
  - `_docs/_VISION/README.md`

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q -k "silhouette_analysis_selects_matching_focus_capture or compare_current_view_does_not_double_apply_persisted_view_adjustments or holds_build_when_role_group_is_incomplete"`
  - result on this machine: `3 passed`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py -q`
  - result on this machine: `92 passed`
- `poetry run mypy`
  - result on this machine: passed
- `PYTHONPATH=. poetry run pytest tests/unit/ -q`
  - result on this machine: `3078 passed`
- `poetry run ruff check server/adapters/mcp/session_capabilities.py server/adapters/mcp/areas/reference.py tests/unit/adapters/mcp/test_reference_images.py`
  - result on this machine: passed
