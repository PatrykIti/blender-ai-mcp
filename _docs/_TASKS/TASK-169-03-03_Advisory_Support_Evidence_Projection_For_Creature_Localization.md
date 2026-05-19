# TASK-169-03-03: Advisory Support Evidence Projection For Creature Localization

**Parent:** [TASK-169-03](./TASK-169-03_Creature_Quality_Bar_Gate_Normalization_And_Advisory_Support_Evidence.md)
**Status:** ✅ Done
**Completed:** 2026-05-19
**Priority:** 🟠 High
**Objective:** Clarify and tighten where optional classifier and segmentation support may improve creature localization while remaining advisory-only on the current RU and compare seams.
**Repository Touchpoints:** `server/adapters/mcp/vision/reference_support.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/vision/runtime.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/unit/adapters/mcp/test_vision_runtime_config.py`
**Acceptance Criteria:**
- optional classifier/segmentation evidence remains default-off and advisory-only
- the task defines where that support should improve creature localization
  without becoming gate authority
- RU-side and compare-time support projections stay consistent on existing
  runtime seams

## Implementation Notes

- keep support evidence split by the current owners:
  - RU-side optional support in `reference_support.py`
  - compare-time packet-local support in `reference_compare_packets.py`
- this slice is about projection, prioritization, and regression clarity, not
  about making the sidecars mandatory

## Runtime / Security Contract Notes

- support evidence must not pass gates on its own
- sidecar unavailability must remain non-fatal and bounded
- do not expose raw mask bytes or private local paths on public payloads

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_reference_compare_packets.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Completion Summary

- RU-side classifier scores and compare-time segmentation support remain
  explicitly advisory-only and non-fatal when unavailable
- the shipped support-evidence surfaces keep those optional signals bounded and
  machine-readable without turning them into gate authority

## Status / Board Update

- closed with parent `TASK-169-03`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_vision_runtime_config.py -q`

## Validation Category

- advisory support-evidence projection proof
