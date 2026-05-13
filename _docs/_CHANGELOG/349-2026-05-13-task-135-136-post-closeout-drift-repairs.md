# 349. TASK-135/TASK-136 post-closeout drift repairs

Date: 2026-05-13

Task: `TASK-135`, `TASK-136`

## Summary

Closed the post-closeout drift audit for the already-shipped reference-guided
creature and architecture reconstruction slices. The repairs keep the public
guided surface on the existing reference, staged-checkpoint, quality-gate, and
visibility contracts without adding new public tools or parallel discovery
paths.

## Changes

- Kept `refine_low_poly_forms` on the existing `reference_images(...)`,
  `reference_compare_stage_checkpoint(...)`, and
  `reference_iterate_stage_checkpoint(...)` surfaces while still blocking
  primary-mass and finish-heavy tools.
- Prevented shape/profile/opening recovery recommendations from leaking while
  unresolved attachment seam or support-contact blockers must be handled first.
- Refreshed `macro_adjust_segment_chain_arc(...)` search metadata so
  refinement-stage creature profile queries continue to surface the bounded
  arc/profile macro after the reference checkpoint tools stay visible.
- Treated successful `modeling_convert_to_mesh(...)` and
  `modeling_set_origin(...)` results as guided spatial mutations so stale
  spatial state re-arms inspection before later gate decisions.
- Broadened architecture guided-goal detection to cover photo-reference wording
  such as "photo references" and "reference photos" across router, prompt, and
  visibility entry points.
- Prioritized `opening_wall` staged truth when trimming architecture reference
  evidence bundles for facade-opening gates.
- Aligned `TASK-135` and `TASK-136` closeout docs with the shipped child-task,
  changelog, and validation evidence.

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_prompt_catalog.py::test_recommended_prompt_entries_can_use_architecture_photo_reference_context -q` (`3 passed`)
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_policy.py::test_profile_recovery_gates_wait_behind_unresolved_seam_or_support_gate tests/unit/adapters/mcp/test_context_bridge.py::test_route_tool_call_marks_guided_spatial_state_stale_after_modeling_refinement_success -q` (`10 passed`)
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_search_surface.py::test_refinement_profile_search_surfaces_bounded_mesh_tools_for_low_poly_creature_queries -q` (`1 passed`)
- `PYTHONPATH=. poetry run pytest ./tests/unit` (`3401 passed`)
- `poetry run python scripts/run_e2e_tests.py` (`476 passed, 3 skipped`; log: `tests/e2e/e2e_test_PASSED_20260513_030347.log`)
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure` (`passed` after ruff-format normalized one file on the first attempt)
- `git diff --check` (`passed`)
