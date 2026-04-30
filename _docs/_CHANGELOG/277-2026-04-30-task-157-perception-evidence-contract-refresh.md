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
- tightened the audit wording so bounded Vision/perception payloads are
  proposal/support refs only, while scene/spatial/mesh/assertion remains the
  gate pass/fail truth layer
- clarified the normative Vision roadmap so `vision_contract_profile` remains
  routing/provenance context, `mesh_edit`/`material_finish` are not new
  canonical planner families, and `mesh_shade_flat`/`macro_low_poly_*` names
  remain future candidates until implemented
- tightened TASK-157 implementability notes so the intake surface starts on the
  existing guided/reference payloads, support-contact visibility names current
  tools, and E2E pseudocode asserts normalized gates instead of legacy required
  role mirrors
- aligned intake and E2E pseudocode with current live seams by using
  `state.goal` / `guided_flow_state` and naming `TASK-157-03` gate response
  fields as new checkpoint-contract additions
- tightened the post-audit `TASK-157` boundary so provider/profile diagnostics
  and VLM compare findings stay provenance/support context, while gate pass/fail
  must cite server-owned scene/spatial/mesh/assertion evidence
- aligned `TASK-157-03` implementability notes with the current centralized
  guided dirtying/finalizer path in `session_capabilities.py` and
  `router_helper.py`
- clarified that pre-build `reference_understanding` remains future/proposed
  until the reference-understanding/gate-proposal contract ships
- reinforced the Vision roadmap as the normative bridge for long-form strategy
  aliases such as `mesh_edit`, `material_finish`, `mesh_shade_flat`, and
  `macro_low_poly_*`

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
