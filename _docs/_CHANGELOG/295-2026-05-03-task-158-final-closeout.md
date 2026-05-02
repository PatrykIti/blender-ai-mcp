# 295. TASK-158 final closeout

Date: 2026-05-03

## Summary

- closed the full `TASK-158` umbrella after both scopes were completed:
  - Scope A documentation/boundary alignment
  - Scope B bounded reference-understanding and default-off optional-perception
    runtime work
- confirmed `TASK-140*` remained a canonical no-op for this wave: no wording
  patch was required to preserve the provider/profile evidence boundary
- synchronized the final `TASK-158` state across:
  - `_docs/_TASKS/TASK-158_Vision_And_Creature_Gate_Boundary_Doc_Alignment.md`
  - `_docs/_TASKS/TASK-158-01*`
  - `_docs/_TASKS/TASK-158-02*`
  - `_docs/_TASKS/TASK-158-03*`
  - `_docs/_TASKS/README.md`
  - `_docs/_CHANGELOG/README.md`
- the long-form Vision plan now reads as historical strategy material where it
  uses draft public-surface names, obsolete owner sketches, or future tool
  candidates, while the runtime and E2E coverage now prove the implemented
  `reference_understanding` seam on existing guided/reference surfaces

## Validation

- `git diff --check`
- `rg -n "quality-gate verifier evidence|provider/profile support evidence|vision_contract_profile" _docs/_TASKS/TASK-140*.md _docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `rg -n "scene/spatial/mesh/reference evidence|true attachment errors|true cleanup/intersection errors|reference evidence requires" _docs/_TASKS/TASK-135*.md`
- `rg -n "reference_understand|router_apply_reference_strategy|server/adapters/mcp/router|mesh_edit|material_finish|mesh_shade_flat|macro_low_poly|macro_create_part|SAM|CLIP|SigLIP|GroundingDINO|OWL-ViT" _docs/blender-ai-mcp-vision-reference-understanding-plan.md`
- Blender-backed outside-sandbox run:
  `poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py::test_reference_understanding_transport_roundtrip_over_stdio tests/e2e/integration/test_guided_gate_state_transport.py::test_reference_understanding_transport_roundtrip_over_streamable tests/e2e/vision/test_reference_understanding_runtime_surface.py tests/e2e/vision/test_reference_understanding_fixture_only_harness.py tests/e2e/vision/test_reference_stage_silhouette_contract.py -q`
  - result on this machine: `5 passed`
