# 387. TASK-179-01 addon object-ID mask render pass

Date: 2026-05-30

## Summary

Implemented the second slice of `TASK-179-01`: a deterministic, headless-safe,
fully reversible **per-object-ID mask render pass** on the Blender addon, wired
through RPC on both sides. This yields per-object masks (each registered part as a
distinct grayscale band) plus an index→name map, with **no external segmentation
model** — the substrate the Set-of-Mark overlays (`TASK-180`) and per-object IoU
(`TASK-179-02`) consume.

## Changes

- `blender_addon/application/handlers/scene_viewport_mixin.py`: new
  `get_object_id_pass(object_names, width, height, camera_name)` — assigns each
  requested object a unique `pass_index` (1..N), enables the view-layer Object
  Index pass, and composites per-object ID Mask nodes into a single grayscale
  image where each object occupies a distinct band. Returns
  `{"image": <base64 PNG>, "index_map": {index: name}, "missing": [...]}`. Fully
  reversible: render engine, resolution, filepath/format/color-mode, camera,
  `use_pass_object_index`, `use_compositing`, `use_nodes`, **every touched
  object's `pass_index`**, and object mode are saved/restored in a `finally`
  block. Returns a clear error string when no usable camera/object is available.
- `blender_addon/__init__.py`: registered `scene.get_object_id_pass` (foreground +
  background).
- `server/application/tool_handlers/scene_handler.py`: added the `get_object_id_pass`
  RPC bridge returning the dict envelope (or the error string).

## Tests

- `tests/e2e/tools/scene/test_scene_get_object_id_pass.py` (Blender-backed):
  - two real objects yield a valid PNG mask + a 1-based index→name map for both
  - a missing object name is reported in `missing` while present ones resolve
  - the pass restores render engine/resolution/format/color-mode (reversible)
- validated against the full `run_e2e_tests.py` cycle on Blender 4.5.1; `ruff` and
  server-side `mypy` clean

## Follow-on

With depth (changelog 386) and object-ID masks now in place, `TASK-179-01`'s
remaining piece is the optional normal pass; `TASK-179-03` (auxiliary-channel
transmission of these images to the VLM) and `TASK-180-02` (stable cross-view
mark ids keyed to the registry, consuming this object-ID map) build directly on
this.

## Research Basis

SpatialRGPT (arXiv:2406.01584): per-part masks/depth alongside the RGB render
sharply improve VLM spatial grounding. Set-of-Mark (arXiv:2310.11441): numbered
marks need a per-object mask source — provided here without SAM. Re-measure on
`tests/fixtures/vision_eval`.
