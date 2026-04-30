# 277. TASK-157 perception evidence contract refresh

Date: 2026-04-30
Version: -

## Summary

- refined the open `TASK-157` gate substrate to reserve typed proposal,
  provenance, evidence-requirement, evidence-ref, and verifier-strategy fields
  for reference-understanding and perception-derived inputs
- clarified that `reference_understanding`, silhouette metrics, optional
  segmentation, future CLIP-style classification, and VLM compare findings may
  seed gate proposals or bounded evidence but cannot mark gates complete
- added evidence-authority rules so scene/spatial/mesh/assertion outputs remain
  authoritative for object existence, contact, measurements, and final
  completion
- aligned `TASK-135` and `TASK-135-03` so low-poly creature refinement consumes
  `TASK-157` evidence refs without pulling SAM/CLIP into the baseline
- clarified the `TASK-140` boundary so external model-family support evidence
  remains separate from quality-gate verifier evidence
- added `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` as the canonical
  Vision-layer roadmap that turns the long-form research plan into repo-owned
  boundaries, MVP scope, phased adapters, and task ownership
- linked that roadmap from the task board's strategic working docs section so
  it stays visible while `TASK-157`, `TASK-135`, and `TASK-140` are active
- refined the post-`f1c23f4` `TASK-157` task family with explicit non-goals,
  runtime/security contract notes, validation commands, changelog-impact lanes,
  and a current guided-family vocabulary note for gate-driven visibility

## Validation

- `git diff --check`
  - result on this machine: passed
- targeted consistency grep for `reference_understanding`, `part_segmentation`,
  `classification_score`, `mesh_edit`, `material_finish`, `mesh_shade_flat`,
  `macro_low_poly`, `SAM`, `CLIP`, and `quality-gate verifier`
  - result on this machine: passed
- manual docs review against
  `_docs/blender-ai-mcp-vision-reference-understanding-plan.md`,
  `_docs/_VISION/README.md`, `TASK-157`, `TASK-135-03`, and `TASK-140`
  - result on this machine: passed
