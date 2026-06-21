# TASK-184-01: Per-Model Set-Of-Mark Overlay Gating

**Parent:** [TASK-184](./TASK-184_Vision_3D_Understanding_Audit_Corrections.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Require explicit model/runtime support before emitting Set-of-Mark overlay captures or mark-heavy response schemas, so small or unknown VLMs are not asked to reason over numbered marks they cannot reliably use.

**Repository Touchpoints:** `server/adapters/mcp/vision/config.py`, `server/adapters/mcp/vision/model_profiles/`, `server/adapters/mcp/vision/runtime.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `tests/unit/adapters/mcp/test_vision_runtime_config.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`

## Implementation Notes

- Add an explicit model capability such as `marks_supported` or
  `visual_mark_overlays_supported` to the existing model capability/profile
  contract rather than creating a parallel registry.
- Overlay emission must require:
  - global operator/config enablement
  - compatible compare stage/preset
  - explicit positive model/runtime mark support
- Unknown, unreviewed, or weak/local models must default to no mark overlay and
  a lean schema.
- Strong reviewed profiles may opt in only when the model has grounding or
  reliable visual-reference capability and enough completion-token budget for
  mark-keyed findings.

## Runtime / Security Contract Notes

- mark overlays remain advisory and default-off unless both runtime and model
  capabilities allow them
- the capability must not be inferred from semantic confidence or provider name
  alone
- external-provider payloads must still redact internal/debug metadata according
  to the existing vision runtime policy

## Tests To Add/Update

- unit coverage for model profile defaults, operator override precedence, and
  unknown-model fallback
- staged compare tests proving overlay images and mark-keyed schema fields are
  omitted when capability is absent
- docs/public-surface tests for the new capability field if the repo already
  validates capability docs

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `TASK-180` historical follow-on note if needed

## Acceptance Criteria

- global `VISION_MARK_OVERLAY_ENABLED` alone cannot cause overlay captures for a
  model whose profile does not support marks
- the response payload explains why marks are unavailable when disabled by model
  capability
- reviewed mark-capable models can still receive overlays when the operator flag
  and stage policy allow them

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_reference_compare_packets.py -q`
