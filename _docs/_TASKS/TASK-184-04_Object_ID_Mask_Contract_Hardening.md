# TASK-184-04: Object-ID Mask Contract Hardening

**Parent:** [TASK-184](./TASK-184_Vision_3D_Understanding_Audit_Corrections.md)
**Status:** ✅ Done
**Completion Date:** 2026-06-22
**Completion Summary:** Hardened object-ID contracts and support evidence around whole-object visible-surface Object Index / `pass_index` masks. The sidecar and per-object metrics now report grayscale-band encoding, object count, high-count quantization risk, missing entries, fragmented visible components, and explicit Cryptomatte deferral.
**Priority:** 🟡 Medium
**Objective:** Make the object-ID evidence contract and docs precise about what the current pass-index mask path proves, what it does not prove, and whether a Cryptomatte upgrade is worth a separate implementation task.

**Repository Touchpoints:** `blender_addon/application/handlers/scene_viewport_mixin.py`, `server/adapters/mcp/vision/silhouette.py`, `server/adapters/mcp/areas/reference_silhouette.py`, `server/adapters/mcp/contracts/reference.py`, `tests/unit/adapters/mcp/`, `tests/e2e/vision/`, `_docs/_VISION/README.md`, `_docs/_MCP_SERVER/README.md`

## Implementation Notes

- Document the current shipped path as object-level Object Index / `pass_index`
  evidence.
- Add tests or fixtures for practical limits:
  - high object counts and grayscale/quantization risk
  - fragmented visible components
  - transparent/material edge cases if supported by the current render path
- Do not claim that normal opaque overlap corrupts both masks unless tests show
  the visible-surface pass behaves that way.
- Treat Cryptomatte as an optional feasibility branch. If it is selected, create
  a later implementation leaf with explicit Blender compositor/version proof.

## Runtime / Security Contract Notes

- object-ID masks are deterministic support evidence, not semantic
  segmentation
- pass-index pixels must not be described as mesh-polygon IDs, semantic parts,
  or per-pixel mesh lookup
- any Cryptomatte payload must stay local/render-derived and must preserve the
  same advisory evidence boundary

## Tests To Add/Update

- unit tests for object-ID metadata and unsupported-field rejection
- E2E or fixture tests for pass-index mask limits where practical
- consistency grep preventing docs from saying object-ID is polygon-level
  evidence

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `TASK-179` historical follow-on note

## Acceptance Criteria

- docs and contracts clearly state object-level pass-index evidence
- known limitations are represented in metadata or task follow-ons
- any Cryptomatte work is either explicitly deferred or split into its own
  implementation task

## Validation Commands

- `git diff --check`
- run the TASK-184 object-ID forbidden-phrase guard over `_docs`, `server`, and
  `tests`

## Validation Run

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_silhouette.py tests/unit/adapters/mcp/test_vision_evaluation.py tests/unit/scripts/test_script_tooling.py -q` -> 94 passed
- TASK-184 object-ID forbidden-phrase guard over `server` and `tests` -> no
  matches
- `git diff --check` -> passed
