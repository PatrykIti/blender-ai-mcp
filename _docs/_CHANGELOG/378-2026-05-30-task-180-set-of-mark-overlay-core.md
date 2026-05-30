# 378. TASK-180 Set-of-Mark overlay core

Date: 2026-05-30

## Summary

Implemented the deterministic, server-side core of `TASK-180` (subtask
`TASK-180-01`): high-contrast numbered marks drawn on a render at the position of
each registered part, so the VLM can refer to a part by a stable mark id instead
of guessing which of several similar parts is meant. Marks are computed from
per-object silhouette masks (e.g. isolated renders) and drawn with PIL — no GPU
overlay code in the addon and no external segmentation model on the render side.

## Changes

- new `server/adapters/mcp/vision/marks.py`:
  - `mask_centroid(mask_image_path)` — integer (x, y) centroid of a silhouette
    mask, reusing the same deterministic mask extraction as the silhouette metrics
  - `overlay_numbered_marks(base_image_path, marks, output_path)` — draws filled
    high-contrast red discs with white outlines and centered white ids (BLINK-style
    high-contrast markers); deterministic and order-stable
  - `build_marks_from_object_masks(object_mask_paths)` — assigns 1-based mark ids
    in sorted object-name order (stable across views/iterations) and skips objects
    whose mask has no usable foreground
  - `render_object_masks(scene_handler, object_names, ...)` — renders each object
    isolated from a shared view via the existing addon `isolate_object` /
    `set_standard_view` / `get_viewport` (no new addon render code), so the
    per-object centroids align with a base capture from that same view
  - `build_object_mark_overlay(scene_handler, ...)` — end-to-end orchestration:
    render per-object masks, assign stable marks, overlay them on the base capture;
    returns `(overlay_path_or_None, mark_id_to_object)`

## Tests

- `tests/unit/adapters/mcp/test_vision_marks.py`: centroid of a centered
  rectangle, None for a blank image, red marks drawn at the requested positions
  with far pixels untouched, stable sorted 1-based id assignment that skips empty
  masks, and the `build_object_mark_overlay` orchestration over a mock scene
  handler (per-object isolated renders -> stable ids -> overlay; None when no mask
  is usable)
- `ruff` and `mypy` clean (repo-wide mypy green); full `tests/unit` green

## Follow-on (needs Blender addon + E2E)

The `build_object_mark_overlay` orchestration is implemented and unit-tested
against a mock scene handler; wiring it into the live compare/capture flow and
confirming the per-object centroids align with the base capture still needs
validation through `run_e2e_tests.py` against real Blender geometry. `TASK-180-02`
stable cross-view/iteration ids keyed to the part registry, `TASK-180-03`
reference-image marks via the default-off Grounded-SAM sidecar, and `TASK-180-04`
mark-keyed findings + correspondence table + validity retry remain open and build
on this core plus the `TASK-179-01` object-ID pass.

## Research Basis

Set-of-Mark (arXiv:2310.11441) and BLINK (arXiv:2404.12390): numbered,
high-contrast marks give VLMs a stable handle to reference specific regions.
Re-measure on `tests/fixtures/vision_eval` before claiming gains.
