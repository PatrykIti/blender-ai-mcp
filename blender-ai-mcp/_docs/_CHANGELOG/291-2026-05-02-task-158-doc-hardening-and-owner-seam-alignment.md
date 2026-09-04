# 291. TASK-158 doc hardening and owner-seam alignment

Date: 2026-05-02

## Summary

- hardened the `TASK-158` umbrella so it now uses `Follow-on After` for the
  closed `TASK-157` substrate and no longer points future closeout work at the
  already-occupied changelog slot `279`
- re-anchored `TASK-158-04` to the live `ingest_quality_gate_proposal[_async]`
  seam, the current `quality_gates.py` result shape, the shared
  `vision/prompting.py` / `vision/parsing.py` / `vision/backends.py` owners,
  and the real guided/router/public-surface integration lanes
- re-anchored `TASK-158-05` to the existing `tests/fixtures/vision_eval/`
  golden-fixture tree, the current live-backend default semantics in
  `scripts/vision_harness.py`, and the explicit disabled/unavailable
  `part_segmentation` envelope already shipped on compare/iterate surfaces
- aligned adjacent source-of-truth docs so implementers no longer read the old
  `TASK-157 later...` future-tense wording or the old creature truth-boundary
  claims as the current contract
- documented the planned `TASK-158` Scope B owner lanes in `_docs/_TESTS/README.md`
  without promoting them as already-shipped proof

## Validation

- `git diff --check`
- `rg -n "\\*\\*Follow-on After:\\*\\*|279-\\.\\.\\.task-158|ingest_llm_gate_proposal|proposal_refs|tests/fixtures/reference_understanding" _docs/_TASKS/TASK-158*.md _docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md _docs/blender-ai-mcp-vision-reference-understanding-plan.md`
  - result on this machine: only the intended `Follow-on After` field remains
- `rg -n "scene/spatial/mesh/reference evidence|true attachment errors|true cleanup/intersection errors|reference evidence requires" _docs/_TASKS/TASK-135*.md`
  - result on this machine: no hits
