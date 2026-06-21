# TASK-184-04: Object-ID Mask Contract Hardening

**Parent:** [TASK-184](./TASK-184_Vision_3D_Understanding_Audit_Corrections.md)
**Status:** ⏳ To Do
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
- object-ID pixels must not be described as face IDs, semantic parts, or
  pixel-to-face lift
- any Cryptomatte payload must stay local/render-derived and must preserve the
  same advisory evidence boundary

## Tests To Add/Update

- unit tests for object-ID metadata and unsupported-field rejection
- E2E or fixture tests for pass-index mask limits where practical
- consistency grep preventing docs from saying object-ID is face-level evidence

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
- `rg -n "object-ID.*face|pixel.*face|Cryptomatte.*shipped|semantic part.*object-ID" _docs server tests`
