# 347. TASK-135 refinement closeout and quadruped genericity

Date: 2026-05-12

Task: `TASK-135-03-03`, `TASK-135`

## Summary

Shipped the remaining bounded `TASK-135` refinement implementation work by
proving the existing-tool profile cases in Blender, superseding the optional
profile-macro leaf, and removing the last squirrel-only goal-classification
drift from the creature handoff path.

## Changes

- Added `tests/e2e/tools/mesh/test_creature_profile_cases.py` to prove body
  mass profiling, ear pointing, and snout wedging on the shipped mesh tool
  surface.
- Added a refinement-search regression that keeps low-poly body/ear/limb/snout
  /tail queries on bounded mesh/profile tools instead of reopening primitive or
  finish-heavy paths.
- Expanded common quadruped creature hints across guided handoff selection,
  guided flow domain selection, prompt recommendation, and refinement domain
  classification so beaver/dog/cat goals stay on the same creature contract as
  squirrel runs.
- Added unit coverage for common quadruped goal classification and generic
  creature gate-template reuse across squirrel, beaver, dog, and cat wording.
- Updated the Blender E2E runner so addon reinstall no longer depends on the
  crash-prone background Blender lane and so one run can fall back to a free
  RPC port when `8765` is already occupied.
- Closed `TASK-135-03-02-01`, `TASK-135-03-02-02`, and `TASK-135-03-02`,
  marked `TASK-135-03-02-03` as superseded because no new profile macro was
  needed, and closed `TASK-135-03-03` / `TASK-135-03` / `TASK-135` after the
  full validation pack cleared.
- Updated `_docs/_TASKS/README.md` and `_docs/_TESTS/README.md` so board state,
  proof lanes, and task hierarchy match the shipped runtime.

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_search_surface.py::test_refinement_profile_search_surfaces_bounded_mesh_tools_for_low_poly_creature_queries -q` (`1 passed`)
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_reference_images.py::test_select_refinement_route_prefers_macro_for_assembly_signals tests/unit/adapters/mcp/test_reference_images.py::test_select_refinement_route_keeps_low_poly_creature_on_modeling_mesh tests/unit/adapters/mcp/test_guided_mode.py::test_guided_mode_refinement_step_keeps_primary_creation_hidden tests/unit/tools/macro/test_macro_adjust_segment_chain_arc.py tests/unit/tools/scene/test_macro_adjust_segment_chain_arc_mcp.py -q` (`87 passed`)
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_prompt_catalog.py tests/unit/adapters/mcp/test_prompt_provider.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_reference_images.py::test_select_refinement_route_prefers_macro_for_assembly_signals tests/unit/adapters/mcp/test_reference_images.py::test_select_refinement_route_prefers_sculpt_for_non_low_poly_organic_refinement tests/unit/adapters/mcp/test_reference_images.py::test_select_refinement_route_keeps_low_poly_creature_on_modeling_mesh tests/unit/tools/macro/test_macro_adjust_segment_chain_arc.py tests/unit/tools/scene/test_macro_adjust_segment_chain_arc_mcp.py -q` (`174 passed`)
- `PYTEST_ADDOPTS="-k 'creature_profile_cases or macro_align_part_with_contact or macro_adjust_segment_chain_arc'" poetry run python scripts/run_e2e_tests.py --skip-build` (`9 passed, 468 deselected`)
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure` (`passed`)
- `PYTHONPATH=. poetry run pytest ./tests/unit -q` (`3363 passed`)
- `uv run --cache-dir /private/tmp/uvcache --active --no-project python -m pytest ./tests/unit -q` (`3362 passed`)
- `uv run python /Users/pciechanski/Documents/_moje_projekty/blender-ai-mcp/scripts/run_e2e_tests.py` from `/private/tmp` (`474 passed, 3 skipped`)
- `git diff --check`
