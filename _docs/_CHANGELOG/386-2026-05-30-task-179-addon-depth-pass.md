# 386. TASK-179-01 addon Z-depth render pass

Date: 2026-05-30

## Summary

Implemented the first slice of `TASK-179-01`: a deterministic, headless-safe,
fully reversible **Z-depth render pass** on the Blender addon, wired through RPC
on both sides. This gives the loop depth/volume geometric evidence that the
single-view 2D silhouette is blind to — two solids that share a silhouette can
now be distinguished by their depth pass.

## Changes

- `blender_addon/application/handlers/scene_viewport_mixin.py`: new
  `get_depth_pass(width, height, camera_name, normalize)` — enables the view
  layer Z pass, builds a minimal compositor graph (RenderLayers Depth → Normalize
  → Invert → Composite) so near surfaces read bright and far/background dark,
  renders via EEVEE (Cycles fallback), and returns the depth image as a base64
  grayscale PNG. It is fully reversible: render engine, resolution, filepath,
  file format, color mode, camera, `use_pass_z`, `use_compositing`, `use_nodes`,
  and object mode are all saved and restored in a `finally` block. Returns a
  clear error string (not a crash) when no usable camera is available.
- `blender_addon/__init__.py`: registered `scene.get_depth_pass` as a foreground
  and background RPC handler (mirroring `scene.get_viewport`).
- `server/application/tool_handlers/scene_handler.py`: added the matching
  `get_depth_pass(...)` RPC bridge method.

## Tests

- `tests/e2e/tools/scene/test_scene_get_depth_pass.py` (Blender-backed):
  - a named-camera depth pass over a real cube returns a valid, non-trivial PNG
  - running the depth pass leaves no side effects (the same viewport render before
    and after is byte-identical — state fully restored)
  - an unknown camera name yields a clear error string, not a crash
- validated against the full `run_e2e_tests.py` cycle on Blender 4.5.1; `ruff` and
  server-side `mypy` clean

## Follow-on

`TASK-179-01` stays In Progress: the object-ID (`pass_index`) mask pass and the
optional normal pass remain, plus `TASK-179-03` auxiliary-channel transmission of
these images to the VLM. The deterministic depth pass is the first of the three
geometric channels.

## Research Basis

SpatialRGPT (arXiv:2406.01584), SD-VLM (arXiv:2509.17664): a depth channel
alongside the RGB render sharply improves VLM spatial grounding over a 2D
silhouette alone. Re-measure on `tests/fixtures/vision_eval`.
