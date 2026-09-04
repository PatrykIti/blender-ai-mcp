# 286. TASK-157 cross-domain gate regression lanes

Date: 2026-05-01

## Summary

- added `tests/e2e/vision/test_goal_derived_gate_creature_completion.py` for a
  Blender-backed creature gate lane that asserts `active_gate_plan`,
  `gate_statuses`, `completion_blockers`, `next_gate_actions`,
  `recommended_bounded_tools`, and `loop_disposition="inspect_validate"`
- extended that creature lane with a repair regression proving the recommended
  attachment macro can clear the seam gate and let `final_completion` pass
- added `tests/e2e/vision/test_goal_derived_gate_building_completion.py` for a
  building/facade gate lane that proves a concrete failed `roof_wall_seam`
  while keeping the missing opening gate unresolved on the same staged
  checkpoint payload surface
- added `tests/e2e/integration/test_guided_gate_state_transport.py` to verify
  `router_set_goal(..., gate_proposal=...)` survives the existing transport
  path through mutation, `scene_relation_graph(...)`, `router_get_status(...)`,
  and `reference_iterate_stage_checkpoint(...)`
- kept the perception boundary on the existing contract surface by asserting a
  typed goal-time policy warning for unavailable required
  `part_segmentation` evidence instead of introducing any new intake flow
- updated task/test docs so `TASK-157-04` now points at the concrete E2E files
  and records that the remaining open proof is environment-dependent execution,
  not missing test ownership

## Validation

- `git diff --check`
- `poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
  - result on this machine: `1 passed, 1 skipped`
- `poetry run pytest tests/e2e/vision/test_goal_derived_gate_creature_completion.py tests/e2e/vision/test_goal_derived_gate_building_completion.py -q`
  - result depends on local Blender RPC/addon availability; the lane is expected
    to `skip` when Blender is unreachable and to exercise the new creature /
    building gate-state checks when RPC is healthy
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_contracts.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/adapters/mcp/test_contract_docs.py tests/unit/adapters/mcp/test_sampling_assistant_docs.py tests/unit/adapters/mcp/test_router_elicitation.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/scene/test_spatial_graph_service.py -q`
  - result on this machine: `321 passed`
