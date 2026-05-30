# 388. TASK-179-01 addon surface-normal render pass

Date: 2026-05-30

## Summary

Implemented the third and final geometric pass of `TASK-179-01`: a deterministic,
headless-safe, fully reversible **surface-normal render pass** on the Blender
addon. With depth (changelog 386) and object-ID masks (changelog 387) already in
place, the addon now exposes the full depth/normal/object-ID geometric trio that
the single-view SOLID capture and 2D silhouette cannot convey.

## Changes

- `blender_addon/application/handlers/scene_viewport_mixin.py`: new
  `get_normal_pass(width, height, camera_name)` — enables the view-layer Normal
  pass and composites the camera-space normal into a viewable RGB image (each axis
  remapped from [-1, 1] to [0, 1] via `n * 0.5 + 0.5`), rendered via Cycles (which
  reliably exposes the `Normal` compositor output socket). Returns a base64 RGB
  PNG. Fully reversible: render engine, resolution, filepath/format/color-mode,
  camera, `use_pass_normal`, `use_compositing`, `use_nodes`, `cycles.samples`, and
  object mode are saved/restored in a `finally` block. Returns a clear error
  string when no usable camera is available.
- `blender_addon/__init__.py`: registered `scene.get_normal_pass` (foreground +
  background).
- `server/application/tool_handlers/scene_handler.py`: added the `get_normal_pass`
  RPC bridge.

## Tests

- `tests/e2e/tools/scene/test_scene_get_normal_pass.py` (Blender-backed): valid
  RGB PNG over a real cube, render-settings reversibility (engine/resolution/
  format/color-mode), and missing-camera error string.
- validated against the full `run_e2e_tests.py` cycle on Blender 4.5.1; `ruff` and
  server-side `mypy` clean.

## Status

This completes the addon render-pass work of `TASK-179-01` (depth + object-ID +
normal, all E2E-validated). The remaining `TASK-179` follow-ons are server-side:
`TASK-179-03` (transmit these auxiliary images to the VLM as labelled captures)
and `TASK-179-02` per-object IoU already consumes the object-ID masks.

## Research Basis

SD-VLM (arXiv:2509.17664), GPTEval3D/3DGen-Bench (arXiv:2401.04092 / 2503.21745):
normal-map channels alongside the RGB render improve VLM 3D-shape understanding.
Re-measure on `tests/fixtures/vision_eval`.
