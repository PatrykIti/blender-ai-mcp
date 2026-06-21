# TASK-184-02: Projection-Based Set-Of-Mark Anchors

**Parent:** [TASK-184](./TASK-184_Vision_3D_Understanding_Audit_Corrections.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Prefer deterministic camera projection diagnostics for live Set-of-Mark anchor placement, using current mask-centroid placement only as a fallback.

**Repository Touchpoints:** `server/adapters/mcp/vision/marks.py`, `server/adapters/mcp/vision/capture_runtime.py`, `blender_addon/application/handlers/scene_viewport_mixin.py`, `server/adapters/mcp/contracts/vision.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/e2e/tools/scene/test_scene_view_diagnostics.py`, `tests/e2e/vision/`

## Implementation Notes

- Reuse the same camera/view used for the transmitted capture.
- Compute mark anchors from Blender projection data first:
  - projected object center when visible and unambiguous
  - projected bbox/representative sample when center is outside but object has
    visible projected extent
  - explicit statuses for `projected`, `outside_frame`, `behind_view`,
    `occluded`, and `unavailable`
- Preserve the current isolate-render/mask-centroid path as a fallback and mark
  that fallback in metadata.
- Avoid adding an extra isolated render per object on the normal path when
  projection diagnostics are sufficient.

## Runtime / Security Contract Notes

- mark anchors are visual prompting support, not geometry truth
- raw coordinates must remain bounded support metadata and should not become the
  primary compare evidence
- failures must degrade by omitting or marking the affected object, not by
  crashing staged compare

## Tests To Add/Update

- unit tests for anchor policy fallback and status normalization
- Blender-backed E2E for projected, outside-frame, and behind-view cases
- regression test proving existing mask-centroid fallback still works when
  projection data is unavailable

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `TASK-180-01` historical note clarifying projection-first follow-on behavior

## Acceptance Criteria

- live mark anchors are projection-first and frame-consistent with the transmitted
  image
- off-frame/behind/unavailable states are explicit in payload metadata
- fallback behavior is visible in diagnostics and does not silently pretend to be
  projection-derived

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/e2e/tools/scene/test_scene_view_diagnostics.py -q`
- `poetry run python scripts/run_e2e_tests.py`
