# TASK-184-05: Depth Auxiliary Caption Encoding Legend

**Parent:** [TASK-184](./TASK-184_Vision_3D_Understanding_Audit_Corrections.md)
**Status:** ✅ Done
**Completion Date:** 2026-06-22
**Completion Summary:** Relative-depth image captions now include `encoding=near_bright_far_dark` beside `channel=relative_depth`, while preserving advisory-only framing and existing budget/drop behavior.
**Priority:** 🟡 Medium
**Objective:** Add the actual relative-depth encoding direction to auxiliary image captions and tests so VLMs and operators do not invert near/far interpretation.

**Repository Touchpoints:** `server/adapters/mcp/vision/prompting.py`, `server/adapters/mcp/vision/capture_runtime.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/contracts/vision.py`, `tests/unit/adapters/mcp/test_vision_prompting.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/unit/adapters/mcp/test_public_surface_docs.py`, `_docs/_VISION/README.md`

## Implementation Notes

- Use the current encoding name `near_bright_far_dark` unless the render path is
  changed at the same time.
- Add caption/payload metadata near the existing `channel=relative_depth`
  language emitted by `format_image_caption(...)`.
- Do not introduce the inverse near-dark/far-bright wording unless the
  underlying encoding changes and tests prove it.

## Runtime / Security Contract Notes

- depth remains relative and advisory
- the caption must not imply metric distance or gate authority
- if a capture is clipped, truncated, or budget-dropped, existing budget
  metadata remains authoritative

## Tests To Add/Update

- unit test for depth auxiliary caption text in `test_vision_prompting.py` and
  structured metadata where packet assembly carries it
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
- grep for the inverse depth legend and for `near_bright_far_dark` in `_docs`,
  `server`, and `tests`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_reference_compare_packets.py -q`

## Validation Run

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_vision_prompting.py -q` -> included in focused TASK-184 run, 160 passed
- TASK-184 forbidden-phrase guard over `server` and `tests` -> no matches
- `git diff --check` -> passed
