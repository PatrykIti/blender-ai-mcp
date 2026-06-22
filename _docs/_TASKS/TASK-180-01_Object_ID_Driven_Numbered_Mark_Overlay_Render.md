# TASK-180-01: Object-ID-Driven Numbered Mark Overlay Render

**Parent:** [TASK-180](./TASK-180_Set_Of_Mark_Object_Bound_Visual_Marks.md)
**Status:** ✅ Done
**Completion Date:** 2026-05-31
**Completion Summary:** The live staged-capture path can now emit default-off `view_kind="overlay"` Set-of-Mark captures for focus presets when `VISION_MARK_OVERLAY_ENABLED=true`. Overlay images are built from deterministic isolate-per-object renders, carry typed `VisionOverlayMarkContract` entries with `placed` / `unmarked` status, stay outside labeled grid composites, and are treated as supplemental packet evidence that drops before primary views when image budgets are tight. Packet payloads include a symbolic mark legend, while mark-keyed result parsing/validity retry remains tracked by `TASK-180-04`. The 2026-06-22 TASK-184 follow-on kept this slice closed while changing live anchors to projection-first placement with mask-centroid fallback metadata.
**Priority:** 🔴 High
**Follow-on After:** [TASK-179](./TASK-179_Blender_Depth_Normal_And_Object_ID_Auxiliary_Passes.md)
**Objective:** Produce a deterministic capture with `view_kind="overlay"` that draws high-contrast numbered marks on registered parts from the staged-capture object set. The live implementation uses isolate-per-object viewport masks to derive projected per-object footprints, while preserving the `TASK-179` object-ID sidecar as the upstream scene-object evidence lane. The render side uses no VLM and no SAM, so the overlay is reproducible from scene state alone.

**Repository Touchpoints:** `server/adapters/mcp/vision/capture_runtime.py`, `server/adapters/mcp/vision/silhouette.py`, `blender_addon/application/handlers/scene_viewport_mixin.py`, `server/adapters/mcp/contracts/vision.py`, `tests/e2e/vision/test_reference_stage_silhouette_contract.py`

**Acceptance Criteria:**
- a new overlay preset (or overlay pass on an existing focus preset) emits a `VisionCaptureImageContract` with `view_kind="overlay"`, finally producing the enum value that `contracts/vision.py:22` already allows but no preset currently uses.
- each registered part in the staged object set either receives exactly one placed numbered mark or is carried as `status="unmarked"` in the typed mark map when no usable foreground footprint can be derived; prompt legends expose only placed/visible marks.
- placed marks are red, ~10px target size, with enough contrast to be legible at the 1280x960 capture resolution.
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
  isolate-render footprint from `vision/marks.py` so the marker centroid is a
  deterministic same-view per-object silhouette centroid, not a VLM or external
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

- `tests/unit/adapters/mcp/test_vision_capture_runtime.py` covers live overlay capture emission, typed mark-id maps, and output artifact creation.
- `tests/unit/adapters/mcp/test_vision_capture_bundle.py` covers overlay metadata propagation and keeping overlay captures outside grid composites.
- `tests/unit/adapters/mcp/test_reference_compare_packets.py` covers overlay packet inclusion without complexity bump and supplemental-first budget dropping.
- `tests/unit/adapters/mcp/test_vision_prompting.py` covers packet mark-legend serialization.
- `tests/unit/adapters/mcp/test_vision_marks.py` covers stable sorted mark ids, including skipped/unmarked objects.
- `tests/e2e/vision/test_set_of_mark_overlay_capture.py` covers real Blender object-set overlay capture and visibility restoration.

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`

## Changelog Impact

- `_docs/_CHANGELOG/392-2026-05-31-task-180-live-mark-overlay-capture.md`

## Status / Board Update

- `_docs/_TASKS/README.md` removes `TASK-180-01` from promoted open Set-of-Mark work.
- `TASK-180` closed on 2026-05-31 after `TASK-180-02`, `TASK-180-03`, and
  `TASK-180-04` landed.

## Validation Commands

- `git diff --check`
- `poetry run ruff check server/adapters/mcp/vision/capture_runtime.py server/adapters/mcp/vision/capture.py server/adapters/mcp/vision/marks.py server/adapters/mcp/vision/prompting.py server/adapters/mcp/vision/backends.py server/adapters/mcp/vision/config.py server/adapters/mcp/vision/runtime.py server/adapters/mcp/areas/reference.py server/adapters/mcp/areas/reference_compare_packets.py server/adapters/mcp/contracts/vision.py server/adapters/mcp/contracts/__init__.py server/infrastructure/config.py tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_capture_runtime.py tests/unit/adapters/mcp/test_vision_capture_bundle.py tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_vision_marks.py tests/e2e/tools/scene/test_scene_get_depth_pass.py tests/e2e/tools/scene/test_scene_get_normal_pass.py tests/e2e/vision/test_set_of_mark_overlay_capture.py`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_capture_runtime.py tests/unit/adapters/mcp/test_vision_capture_bundle.py tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_vision_marks.py -q`
- `PYTEST_ADDOPTS='-k "depth_pass_supports_user_perspective_view or normal_pass_supports_user_perspective_view or set_of_mark_overlay"' poetry run python scripts/run_e2e_tests.py`

## Validation Category

- deterministic overlay-render and visual-prompting proof
