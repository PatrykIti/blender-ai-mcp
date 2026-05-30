# 376. TASK-179 per-object mask IoU primitive

Date: 2026-05-30

## Summary

Implemented the deterministic server-side core of `TASK-179` (subtask
`TASK-179-02`): a per-object silhouette IoU primitive that returns the
bbox-normalized intersection-over-union between two silhouette images. This is
the geometric evidence that lets a mismatch be attributed to a specific
registered part instead of only the whole-frame silhouette, and it reuses the
exact mask extraction/normalization the whole-silhouette metric already uses.

## Changes

- `server/adapters/mcp/vision/silhouette.py`: added `compute_silhouette_iou`,
  which extracts and bbox-normalizes both masks (via the existing
  `_extract_mask_from_image` / `_crop_bbox` / `_normalize_mask`) and returns the
  IoU in [0, 1], or `None` when either mask is unusable.

## Tests

- `tests/unit/adapters/mcp/test_vision_silhouette.py`: identical shapes at
  different positions/sizes normalize to IoU ~1.0; a box vs a triangle yields a
  partial IoU; a blank image returns `None`
- full `poetry run pytest ./tests/unit` green; `ruff` and `mypy` clean

## Follow-on (needs Blender addon + E2E)

`TASK-179-01` (addon object-ID / Z-depth / normal compositor render passes via
RPC) and `TASK-179-03` (auxiliary-channel image transmission with captions)
remain open. They require new `bpy` compositor/render-pass code on the addon
side, RPC both-sides, and validation through `scripts/run_e2e_tests.py`; for
reference parts they also depend on the default-off Grounded-SAM segmentation
sidecar. `TASK-180` (Set-of-Mark overlays) builds on those passes and is likewise
addon + E2E work.

## Research Basis

SpatialRGPT (arXiv:2406.01584), SD-VLM (arXiv:2509.17664): per-part geometric
evidence (masks/depth) sharply improves spatial grounding over whole-frame
silhouette alone. Re-measure on `tests/fixtures/vision_eval` before claiming gains.
