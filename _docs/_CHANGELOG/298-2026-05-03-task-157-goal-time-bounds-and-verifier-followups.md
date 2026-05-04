# 298. TASK-157 goal-time bounds and verifier follow-ups

Date: 2026-05-03

## Summary

- scoped goal-time evidence pruning to `llm_goal` proposals only, so
  `reference_understanding` gate slices can keep runtime-only requirements like
  `part_segmentation` instead of being silently dropped during later guided
  intake
- changed `router_set_goal(...)` to merge same-call `gate_proposal` payloads
  into the already refreshed guided session state, which preserves
  reference-derived gates when attached references and client-supplied goal
  gates arrive in the same request
- tightened relation-pair fallback matching to score candidate object names
  rather than full prose labels, so labels like `tail seated on body` and
  `ear pair stays symmetric` still bind to the correct authoritative pair
- added explicit verifier follow-up states for `shape_profile`,
  `proportion_ratio`, `opening_or_cut`, and `refinement_stage` gates, and made
  routed dirty-state invalidation union affected objects across every
  successful dirty step instead of only the first one

## Validation

- `git diff --check`
- `python3 -m py_compile server/adapters/mcp/session_capabilities.py server/adapters/mcp/areas/router.py server/adapters/mcp/router_helper.py server/adapters/mcp/transforms/quality_gate_verifier.py`
- `poetry run mypy server/adapters/mcp/session_capabilities.py server/adapters/mcp/areas/router.py server/adapters/mcp/router_helper.py server/adapters/mcp/transforms/quality_gate_verifier.py`
  - result on this machine: `Success: no issues found in 4 source files`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --files server/adapters/mcp/session_capabilities.py server/adapters/mcp/areas/router.py server/adapters/mcp/router_helper.py server/adapters/mcp/transforms/quality_gate_verifier.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_reference_images.py tests/e2e/integration/test_guided_gate_state_transport.py tests/e2e/vision/test_goal_derived_gate_building_completion.py`
  - result on this machine: `Passed`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_context_bridge.py -q`
  - result on this machine: `66 passed`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -k 'projects_building_attachment_gate_state or reference_understanding' -q`
  - result on this machine: `4 passed, 76 deselected`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_reference_images.py -k 'reference_understanding or gate or guided_spatial_dirty_tracking_accumulates_objects_from_all_dirty_steps or building_attachment_gate_state' -q`
  - result on this machine: `35 passed, 111 deselected`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -k 'later_goal_gate_proposal_preserves_reference_understanding_gates or same_call_goal_gate_proposal_preserves_reference_understanding_gates' -q`
  - result on this machine: `2 passed, 2 skipped, 10 deselected`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_goal_derived_gate_building_completion.py::test_reference_iterate_stage_checkpoint_blocks_building_gate_completion -q`
  - result on this machine: `1 skipped`
