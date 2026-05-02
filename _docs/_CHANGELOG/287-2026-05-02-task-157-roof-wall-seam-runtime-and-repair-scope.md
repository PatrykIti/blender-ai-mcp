# 287. TASK-157 roof-wall seam runtime and repair scope

Date: 2026-05-02

## Summary

- extended the deterministic attachment-semantics owner path so
  `FacadeRoofMass -> FacadeMainVolume` now resolves to a structural
  `roof_wall` seam in both `scene_relation_graph(...)` truth payloads and the
  staged reference/checkpoint follow-up path
- kept the gate verifier unchanged and let the new structural seam semantics
  drive the intended status transition naturally: a floating roof now degrades
  to `failed / relation_floating_gap` instead of stopping at
  `blocked / missing_relation_pair`
- aligned `reference_compare_stage_checkpoint(...)` with the active goal when
  rebuilding gate relation graphs so guided checkpoint verification uses the
  same deterministic pairing context as the runtime scene-truth path
- fixed the creature repair regression lane by keeping a head mass in the
  active checkpoint scope before asserting `final_completion == passed`, so the
  test now satisfies the full `creature` domain template contract rather than
  only the repaired seam gate
- added unit owner-lane coverage for the new `roof_wall` semantics and the
  staged building gate projection, then refreshed TASK-157 runtime/test docs to
  record the scoped drift repair

## Validation

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_spatial_graph_service.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_quality_gate_verifier.py -q`
  - result on this machine: `85 passed`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_goal_derived_gate_creature_completion.py tests/e2e/vision/test_goal_derived_gate_building_completion.py -q`
  - result on this machine: `3 skipped` because local Blender RPC/addon runtime was unavailable
