# TASK-180-01: Object-ID-Driven Numbered Mark Overlay Render

**Parent:** [TASK-180](./TASK-180_Set_Of_Mark_Object_Bound_Visual_Marks.md)
**Status:** ✅ Done
**Completed:** 2026-05-30
**Priority:** 🔴 High
**Follow-on After:** [TASK-179](./TASK-179_Blender_Depth_Normal_And_Object_ID_Auxiliary_Passes.md)
**Objective:** Produce a deterministic capture with `view_kind="overlay"` that draws high-contrast numbered marks on each registered part, anchored from the `TASK-179` object-ID assignment. The render side uses no VLM and no SAM: marks are placed from the projected per-object footprint of registered scene objects, so the overlay is reproducible from scene state alone.

**Repository Touchpoints:** `server/adapters/mcp/vision/capture_runtime.py`, `server/adapters/mcp/vision/silhouette.py`, `blender_addon/application/handlers/scene_viewport_mixin.py`, `server/adapters/mcp/contracts/vision.py`, `tests/e2e/vision/test_reference_stage_silhouette_contract.py`

**Acceptance Criteria:**
- a new overlay preset (or overlay pass on an existing focus preset) emits a `VisionCaptureImageContract` with `view_kind="overlay"`, finally producing the enum value that `contracts/vision.py:22` already allows but no preset currently uses.
- each registered part in the `TASK-179` object-ID set receives exactly one numbered mark; marks are red, ~10px target size, with enough contrast to be legible at the 1280x960 capture resolution.
- mark placement is deterministic given the scene state: re-running the overlay capture on an unchanged scene yields the same marks at the same anchors.
- the overlay capture carries a typed mark-id map (mark number -> scene `object_name`) so downstream slices can bind findings without re-deriving placement.
- the overlay pass is reversible: it uses `capture_scene_state` / `restore_scene_state` and the addon isolation path, leaving scene visibility and view state unchanged after capture.

## Implementation Notes

- Set-of-Mark prompting (arXiv:2310.11441) is the technique: overlay numbered
  symbolic marks on the image so the model can address regions by ID rather than
  by prose or coordinates. BLINK (arXiv:2404.12390) is the basis for the marker
  style: red markers around ~10px are the most reliably perceived; use that as
  the target marker spec rather than tiny or low-contrast labels.
- The render side stays deterministic. `capture_runtime.py` already isolates
  target objects (`scene_handler.isolate_object(isolate_names)` ~:208) and sets
  standard views; the overlay pass adds, per registered part, a projected anchor
  and a numbered marker. Anchor derivation should reuse the existing per-object
  projection helpers on the addon mixin (`_object_bbox_points`,
  `_object_view_sample_points`, `_project_point_to_camera`,
  `_build_view_target_diagnostic` in `scene_viewport_mixin.py`) so the marker
  centroid is the projected, camera-visible footprint of that object, not a 2D
  segmentation guess.
- `silhouette.py` already has the deterministic component machinery
  (`_largest_component`, `_crop_bbox`, `_extract_mask_from_image`); reuse it when
  a per-object footprint must be refined from a single-object isolated render
  (isolate one object, extract its largest component, take the centroid). This
  keeps the render-side mark placement free of any external model.
- Drawing the markers should happen on the addon main thread as part of (or
  immediately after) `get_viewport`, because that is the only main-thread-safe
  place to read the projected geometry. Two viable shapes:
  1. isolate-per-object renders + composite marks server-side from the typed
     anchors (keeps Blender drawing minimal), or
  2. a single annotated render where the addon draws the markers into the image
     before base64 return.
  Prefer option (1) for testability unless the addon already has a safe overlay
  draw path; either way, update BOTH RPC sides and keep the swallowed-exception
  camera ops (`except Exception: pass` ~:211/216/221/232) from hiding a failed
  isolation that would mis-anchor a mark.
- Fix the silent-failure smell while here: if isolation or projection for a part
  fails, the part must be recorded as "unmarked" in the mark-id map rather than
  silently skipped, so downstream validity logic can see the gap.
- Label convention: keep the existing `f"{preset.name}_{stage}"` label scheme
  (`capture_runtime.py:251`) and add the overlay marker map as typed contract
  data, not as a smuggled label string.

## Pseudocode

```python
def capture_overlay_image(scene_handler, *, bundle_id, stage, registered_parts):
    # registered_parts: ordered [(mark_id:int, object_name:str, role:str|None)]
    original_state = capture_scene_state(scene_handler)
    mark_map: list[VisionOverlayMarkContract] = []
    anchors: dict[int, tuple[float, float]] = {}
    try:
        for mark_id, object_name, _role in registered_parts:
            scene_handler.isolate_object([object_name])
            anchor = scene_handler.project_object_anchor(object_name)  # camera-visible centroid
            if anchor is None:
                mark_map.append(VisionOverlayMarkContract(mark_id=mark_id,
                                                          object_name=object_name,
                                                          status="unmarked"))
                continue
            anchors[mark_id] = anchor
            mark_map.append(VisionOverlayMarkContract(mark_id=mark_id,
                                                      object_name=object_name,
                                                      status="placed"))
        restore_scene_state(scene_handler, original_state)
        b64 = scene_handler.get_viewport(width=1280, height=960, shading="SOLID")
        overlay_b64 = composite_red_numbered_marks(b64, anchors, target_px=10)  # deterministic
        path = write_overlay_artifact(bundle_id, stage, overlay_b64)
        return VisionCaptureImageContract(
            label=f"overlay_{stage}",
            image_path=path,
            preset_name="overlay",
            media_type="image/jpeg",
            view_kind="overlay",
        ), mark_map
    finally:
        restore_scene_state(scene_handler, original_state)
```

## Runtime / Security Contract Notes

- the overlay capture is a deterministic scene-truth artifact, not a vision
  judgment; it does not assert correctness and does not mark gates complete.
- everything stays main-thread-safe and reversible: isolation/projection happen
  under `capture_scene_state` / `restore_scene_state`, and a failed per-object
  isolation must restore state and record the part as `unmarked`, never leave
  the scene in an isolated state.
- no raw box/coordinate tokens leave this slice as primary evidence; the overlay
  exposes only symbolic numbered marks plus the typed mark-id map.
- the mark-id map is advisory input for the VLM, not authority: downstream
  findings keyed to these marks still require deterministic verification.

## Tests To Add/Update

- `tests/e2e/vision/test_reference_stage_silhouette_contract.py` (extend with an overlay-capture assertion that the overlay image is emitted with `view_kind="overlay"` and a non-empty mark-id map)
- new `tests/e2e/vision/test_set_of_mark_overlay_capture.py` (deterministic overlay render for a multi-part scene; one mark per registered part; reversibility)
- `tests/unit/adapters/mcp/` unit lane for the deterministic marker compositing helper (anchor -> red ~10px marker placement)

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- board tracking remains on umbrella `TASK-180`
- no separate promoted board-row change is expected for this subtask

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_stage_silhouette_contract.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`  # Blender/addon overlay-render behavior changes

## Validation Category

- deterministic overlay-render and visual-prompting proof
