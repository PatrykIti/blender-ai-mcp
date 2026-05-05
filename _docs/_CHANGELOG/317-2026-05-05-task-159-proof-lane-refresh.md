# 317. TASK-159 proof-lane refresh

Date: 2026-05-05
Version: -

## Summary

- recalculated `_docs/_TASKS/README.md` statistics after the `TASK-159` /
  `TASK-161` closure wave so the board header matches the real row counts
- added Blender-backed E2E coverage for the post-refactor scene context,
  structural-read, and read-heavy inspect/runtime seams that were still only
  indirectly or unit-level proved after `TASK-159`
- aligned the relevant `TASK-159*` / `TASK-161*` validation lists with the new
  E2E files so future closure audits point at the actual proof lanes
- re-ran the integrated proof lanes on the current checkout to confirm the
  modularized scene/reference/session surfaces are green end-to-end
- fixed the new scene inspect proof-lane test to use the runtime modifier name
  instead of assuming a hard-coded label, then re-ran only the new scene files
  against live Blender RPC to keep the closeout loop fast

## Validation

- `poetry run pytest ./tests/unit`
  - `3206 passed`
- `poetry run python scripts/run_e2e_tests.py`
  - `454 passed, 3 skipped`
- targeted Blender-backed rerun after the scene inspect test fix
  - `poetry run pytest tests/e2e/tools/scene/test_scene_read_runtime_surfaces.py tests/e2e/tools/scene/test_scene_inspect_runtime_surfaces.py -q`
  - `4 passed`
