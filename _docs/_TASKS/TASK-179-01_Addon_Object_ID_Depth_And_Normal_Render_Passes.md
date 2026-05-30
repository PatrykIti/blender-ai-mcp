# TASK-179-01: Addon Object-ID, Depth And Normal Render Passes

**Parent:** [TASK-179](./TASK-179_Blender_Depth_Normal_And_Object_ID_Auxiliary_Passes.md)
**Status:** ✅ Done
**Completed:** 2026-05-30
**Completion Summary:** All three geometric render passes shipped and validated green against real Blender 4.5.1 (E2E 491 passed):
- Z-depth pass (changelog 386): addon `scene.get_depth_pass` (compositor Z pass → normalized grayscale PNG, full save/restore), RPC both sides, server bridge, three E2E tests.
- Object-ID mask pass (changelog 387): addon `scene.get_object_id_pass` — unique `pass_index` per object → Object Index pass → per-object ID-Mask grayscale bands → base64 PNG + index→name map (no SAM), rendered via Cycles (which reliably exposes the `IndexOB` compositor socket), fully reversible incl. each object's `pass_index`; RPC both sides, server bridge returning the dict envelope, three E2E tests.
- Surface-normal pass (changelog 388): addon `scene.get_normal_pass` — camera-space Normal pass remapped to viewable RGB, Cycles-rendered, fully reversible; RPC both sides, server bridge, three E2E tests.

The E2E loop caught three real bugs during development (render-byte reversibility check; EEVEE not exposing `IndexOB`; undefined `original_samples` in the restore block) — all fixed. Follow-on `TASK-179-03` (transmit these auxiliary images to the VLM as labelled captures) remains server-side.
**Priority:** 🔴 High
**Follow-on After:** [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md)
**Objective:** Add an addon-side path (compositor / render passes) that produces a deterministic per-object-ID mask image, a Z-depth image, and an optional normal image for the active camera/view, wired through RPC on both sides and fully reversible via `capture_scene_state` / `restore_scene_state` semantics. The new passes reuse the existing render context that `get_viewport(...)` already manages, do not change the default `SOLID` capture, and produce first-party deterministic masks with no external model.
**Repository Touchpoints:** `blender_addon/application/handlers/scene_viewport_mixin.py`, `blender_addon/application/handlers/scene.py`, `blender_addon/infrastructure/rpc_server.py`, `blender_addon/__init__.py`, `server/application/tool_handlers/scene_handler.py`, `server/adapters/rpc/client.py`, `server/domain/tools/scene.py`, `server/domain/interfaces/rpc.py`, `tests/e2e/vision/test_reference_understanding_runtime_surface.py`, `tests/e2e/integration/test_guided_surface_contract_parity.py`
**Acceptance Criteria:**
- a new addon method (e.g. `scene.get_geometry_passes`) returns, for the active camera/view, a deterministic object-ID mask image plus per-object index map, a normalized Z-depth image, and an optional normal image, all as base64 artifacts in the same envelope style as `get_viewport`
- the object-ID pass assigns a stable, deterministic `pass_index` per requested registered object and reports the index->object-name map so the server can build per-object masks without SAM
- the new path is main-thread-safe and fully reversible: it saves and restores render engine, view layer pass flags, compositor node tree, `pass_index` assignments, resolution, file format, and view state exactly like `get_viewport` already does (`scene_viewport_mixin.py:72-90`, `:241-294`)
- the method is registered on **both** RPC sides (`blender_addon/__init__.py` register + `server/application/tool_handlers/scene_handler.py` mirror) and the server interface/domain tool is updated to match
- when passes are unavailable (no compositor context / headless without EEVEE-Next Z) the method fails closed with a typed `available: False` reason rather than partial garbage

## Implementation Notes

- Reuse the proven render scaffold in
  `blender_addon/application/handlers/scene_viewport_mixin.py:15`
  (`get_viewport`). It already: forces Object Mode (`:36-44`), saves render
  state (`:72-90`), validates shading against `{"WIREFRAME","SOLID","MATERIAL","RENDERED"}`
  (`:99`), runs OpenGL/Workbench/Cycles fallbacks (`:159-223`), and restores
  everything in a `finally` block (`:241-294`). The new geometry-pass method must
  mirror this save/restore discipline; it additionally has to save/restore the
  **view-layer pass enable flags**, the **compositor node tree**
  (`scene.use_nodes` + node graph), and any per-object `pass_index` it sets.
- Object-ID masks: enable `view_layer.use_pass_object_index`, assign a
  deterministic `obj.pass_index` for each requested registered object, render with
  a Workbench/EEVEE pass, and read the Object Index pass through the compositor
  (File Output node) or via the render-result render-pass pixels. Because the
  index map is deterministic per object, the server can derive a clean binary
  mask per part with **no SAM** — this is the key difference from the optional
  TASK-172 segmentation sidecar.
- Z-depth: enable `view_layer.use_pass_z`, render, and emit a **normalized**
  (relative) depth image. Per the family Non-Goals, the depth is relative, not
  metric truth; the server side must surface depth only as a proportional channel.
- Normal pass (optional): enable `view_layer.use_pass_normal`, render, encode as
  an RGB image. Gate this behind a request flag so it does not inflate the
  default payload.
- Determinism / engine choice: prefer the existing Workbench fallback path
  (`scene_viewport_mixin.py:188-208`) for headless safety; only the passes that a
  given engine supports should be emitted, and the method must report which passes
  were produced. Do not silently swallow a missing pass — return a typed reason,
  unlike the broad `except Exception: pass` style at
  `capture_runtime.py:211/216/221/232` on the server side.
- RPC wiring mirrors the existing `scene.get_viewport` round trip:
  registration in `blender_addon/__init__.py` next to
  `rpc_server.register_handler("scene.get_viewport", ...)`, and a server-side
  mirror modeled on `scene_handler.py:44-70` that calls
  `self.rpc.send_request("scene.get_geometry_passes", args)`. Update
  `server/domain/tools/scene.py` (`ISceneTool`) and, if the interface signature
  changes, `server/domain/interfaces/rpc.py`.
- Research basis (cite by name + arXiv id, do not implement chain-of-thought):
  - **SpatialRGPT** — depth connector for spatial VLM reasoning (arXiv:2406.01584).
  - **SD-VLM** — depth encoding contributes +26.9 pts on its benchmark
    (arXiv:2509.17664).
  - **Spatial reasoning survey** — depth as a standard input channel
    (arXiv:2405.10255).
  - **GPTEval3D / 3DGen-Bench** — normal-map passes for 3D quality evaluation
    (arXiv:2401.04092 / arXiv:2503.21745).
  These motivate *which* channels to emit; they do not change the advisory
  boundary, and their gains are not Blender-vs-reference measurements.

## Pseudocode

```python
def get_geometry_passes(self, target_objects, include_normal=False, width=1280, height=960):
    saved = self._save_render_pass_state()  # engine, view_layer passes, node tree, pass_index, view state
    try:
        view_layer = bpy.context.view_layer
        view_layer.use_pass_object_index = True
        view_layer.use_pass_z = True
        view_layer.use_pass_normal = bool(include_normal)

        index_map = {}
        for i, name in enumerate(target_objects, start=1):
            obj = bpy.data.objects.get(name)
            if obj is None:
                continue
            obj.pass_index = i          # deterministic, stable per request
            index_map[i] = name

        render = self._render_with_compositor_passes(width, height)  # Workbench-first, headless-safe
        if render is None:
            return {"available": False, "reason": "geometry_passes_unsupported"}

        return {
            "available": True,
            "object_id_image_b64": render.object_index_png_b64,
            "object_index_map": index_map,        # {pass_index: object_name}
            "depth_image_b64": render.normalized_depth_png_b64,
            "normal_image_b64": render.normal_png_b64 if include_normal else None,
            "produced_passes": render.produced_passes,
        }
    finally:
        self._restore_render_pass_state(saved)   # main-thread-safe, reversible
```

## Runtime / Security Contract Notes

- These passes are **deterministic addon render output**, but everything derived
  from them on the VLM-facing side stays **advisory**: depth/normal/object-ID
  evidence cannot mark a gate complete or unlock a tool, and keeps
  `not_truth_source` / `requires_deterministic_checks_for_correctness` framing.
- Depth is **relative/normalized**, never an authoritative absolute measurement;
  downstream magnitudes must be proportional ratios against a trusted reference
  anchor (VLMs ~37% within 2x on metric tasks).
- The object-ID mask path is first-party and needs **no SAM / no external model**;
  it must not be routed through the TASK-172 optional default-off sidecar seam.
  The only optional-runtime hook in this family (monocular depth for the
  *reference* image) lives in a later slice and stays default-off there.
- All Blender mutation (pass flags, compositor nodes, `pass_index`, engine,
  resolution, view state) must be saved and restored on the main thread; the
  method must leave the scene byte-identical for those fields on exit, matching
  the `get_viewport` finally-block discipline.

## Tests To Add/Update

- `tests/e2e/vision/test_reference_understanding_runtime_surface.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/vision/test_reference_stage_silhouette_contract.py`
- a new unit lane under `tests/unit/adapters/mcp/` for the server-side RPC mirror
  (modeled on existing `scene_handler` viewport coverage) asserting the
  `scene.get_geometry_passes` request shape and the typed `available: False`
  failure path

## Docs To Update

- `_docs/_ADDON/README.md`
- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- board tracking remains on umbrella `TASK-179`
- no separate promoted board-row change is expected for this subtask unless it
  later becomes a standalone follow-on

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_understanding_runtime_surface.py tests/e2e/integration/test_guided_surface_contract_parity.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`

## Validation Category

- addon render-pass producer + RPC parity proof (Blender behavior change)
