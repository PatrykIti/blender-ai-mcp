# 294. TASK-158 Scope A doc alignment and E2E drift hardening

Date: 2026-05-03

## Summary

- closed `TASK-158-01` by finishing the long-form
  `blender-ai-mcp-vision-reference-understanding-plan.md` cleanup:
  draft `reference_understand(...)` / `router_apply_reference_strategy(...)`
  language now stays explicitly historical, current shared owners are listed
  first, and low-poly macro/tool names remain future candidates instead of
  implied current surface
- closed `TASK-158-02` as a validated no-op docs closeout because the current
  `TASK-135*` wording already matches the `TASK-157` verifier/truth boundary
- fixed the `TASK-158` Scope B drift where reference-understanding proposals
  could replace an existing gate plan instead of augmenting it
- added exact transport and Blender-backed E2E coverage for
  `reference_understanding_summary`, `reference_understanding_gate_ids`, and
  the `part_segmentation` envelope, and added subprocess E2E coverage for
  `scripts/vision_harness.py --fixture-only reference-understanding`
- updated the umbrella board/progress notes so `TASK-158` now tracks only the
  remaining `TASK-158-03` closeout lane as open

## Validation

- `git diff --check`
- `rg -n "scene/spatial/mesh/reference evidence|true attachment errors|true cleanup/intersection errors|reference evidence requires" _docs/_TASKS/TASK-135*.md`
- `rg -n "reference_understand|router_apply_reference_strategy|server/adapters/mcp/router|mesh_edit|material_finish|mesh_shade_flat|macro_low_poly|macro_create_part|SAM|CLIP|SigLIP|GroundingDINO|OWL-ViT" _docs/blender-ai-mcp-vision-reference-understanding-plan.md`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py::test_reference_understanding_transport_roundtrip_over_stdio tests/e2e/integration/test_guided_gate_state_transport.py::test_reference_understanding_transport_roundtrip_over_streamable tests/e2e/vision/test_reference_understanding_runtime_surface.py tests/e2e/vision/test_reference_understanding_fixture_only_harness.py tests/e2e/vision/test_reference_stage_silhouette_contract.py -q`
  - final Blender-backed outside-sandbox run result on this machine: `5 passed`
