# 288. TASK-157 correction-truth alignment and transport regression

Date: 2026-05-03

## Summary

- aligned staged `truth_bundle`, `truth_followup`, and `correction_candidates`
  with the same guided pair-expansion owner path that feeds `active_gate_plan`,
  so goal-sensitive `support_contact` and `symmetry_pair` evidence no longer
  disappears from correction-truth surfaces
- widened correction-truth item kinds and planner blockers to treat support and
  symmetry findings as first-class structural signals, which keeps inspect /
  repair handoff aligned with the verifier-owned gate contract
- neutralized attachment follow-up and macro wording so `roof_wall` and other
  non-creature seams no longer surface organic-creature prose in staged repair
  guidance
- preserved flattened iterate gate fields from `compare_result` when no
  `active_gate_plan` is present, closing the latent drift between
  `loop_disposition` escalation and the returned top-level gate summary fields
- upgraded the transport regression to execute the real staged compare path
  instead of a stub, including attached references, deterministic staged
  captures, and gate-plan verification through the transport surface
- removed `final_completion` from the machine-readable blocker aggregation so
  staged responses now surface only concrete required blockers instead of the
  aggregate gate duplicating them
- fixed support-pair macro propagation from `truth_followup` into
  `correction_candidates` and added public compare-stage symmetry coverage plus
  extra transport coverage beyond the creature attachment seam lane
- refreshed task/test/changelog docs so the repo no longer describes live
  Blender proof as the last missing closeout item for the current TASK-157
  owner slice

## Validation

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_contracts.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/scene/test_spatial_graph_service.py -q`
  - result on this machine: `202 passed`
- `poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py tests/e2e/vision/test_goal_derived_gate_creature_completion.py tests/e2e/vision/test_goal_derived_gate_building_completion.py -q`
  - result on this machine: `7 passed`
