# TASK-184-05: Depth Auxiliary Caption Encoding Legend

**Parent:** [TASK-184](./TASK-184_Vision_3D_Understanding_Audit_Corrections.md)
**Status:** ⏳ To Do
**Priority:** 🟡 Medium
**Objective:** Add the actual relative-depth encoding direction to auxiliary image captions and tests so VLMs and operators do not invert near/far interpretation.

**Repository Touchpoints:** `server/adapters/mcp/vision/capture_runtime.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/contracts/vision.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/unit/adapters/mcp/test_public_surface_docs.py`, `_docs/_VISION/README.md`

## Implementation Notes

- Use the current encoding name `near_bright_far_dark` unless the render path is
  changed at the same time.
- Add caption/payload metadata near the existing `channel=relative_depth`
  language.
- Do not introduce the opposite `near_dark_far_bright` wording unless the
  underlying encoding changes and tests prove it.

## Runtime / Security Contract Notes

- depth remains relative and advisory
- the caption must not imply metric distance or gate authority
- if a capture is clipped, truncated, or budget-dropped, existing budget
  metadata remains authoritative

## Tests To Add/Update

- unit test for depth auxiliary caption text and structured metadata
- docs/public-surface test if auxiliary caption examples are validated
- consistency grep for the wrong encoding string

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `TASK-179-03` historical follow-on note if needed

## Acceptance Criteria

- every transmitted relative-depth auxiliary image carries an explicit
  `near_bright_far_dark` legend
- tests fail if the inverse legend appears in current docs or caption helpers

## Validation Commands

- `git diff --check`
- `rg -n "near_dark_far_bright|near_bright_far_dark" _docs server tests`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py -q`
