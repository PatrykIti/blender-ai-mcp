# TASK-177-03: Optional Labeled Multi-View Grid Composite

**Parent:** [TASK-177](./TASK-177_Reachable_Rich_Multi_View_Capture_And_Top_View_Default.md)
**Status:** ✅ Done
**Completed:** 2026-05-30
**Completion Note:** Deterministic labelled grid composite (`build_labeled_view_grid`) shipped in changelog 384 and live capture-path wiring shipped in changelog 389. The path is default-off behind `VISION_CAPTURE_GRID_ENABLED`, surfaces `VisionRuntimeConfig.capture_grid_enabled`, emits `view_kind="grid"` captures, preserves grid captions through `VisionImageInput.view_kind`, and replaces transmitted selected views with the bounded grid image when enabled.
**Priority:** 🟢 Low
**Follow-on After:** [TASK-177-01](./TASK-177-01_Decouple_Capture_From_Transmission_And_Budget_Aware_Selection.md), [TASK-177-02](./TASK-177-02_Orthographic_Top_And_Oblique_Default_Capture_Presets.md)
**Objective:** Optionally composite the selected views into a single labeled grid image (IG-VLM style) for models/budgets where one annotated montage outperforms many separate images, behind a default-off config flag, with each cell labeled by its view kind and captioned per [TASK-174](./TASK-174_Per_Image_Caption_Interleaving_For_Vision_Payloads.md).
**Repository Touchpoints:** `server/adapters/mcp/vision/capture_runtime.py`, `server/adapters/mcp/vision/capture.py`, `server/adapters/mcp/vision/config.py`, `server/infrastructure/config.py`, `server/adapters/mcp/contracts/vision.py`, `tests/unit/adapters/mcp/test_vision_runtime_config.py`, `tests/unit/adapters/mcp/test_vision_capture_runtime.py`, `tests/unit/adapters/mcp/test_vision_capture_bundle.py`
**Acceptance Criteria:**
- a default-off config flag (e.g. `VISION_CAPTURE_GRID_ENABLED`) controls whether
  the selected captures are composited into one labeled grid image; when off, the
  current per-image bundle behavior is unchanged
- when on, the selected views (from `TASK-177-01` selection, including the
  `TASK-177-02` top/oblique) are arranged into one deterministic grid image with
  each cell visibly labeled by its view kind / preset name
- the grid composite respects the same bounded image budget: it ships as one
  transmitted image (or a small fixed number) and never pushes the request past
  `runner.py:170-179`
- the grid image is exposed as a `VisionCaptureImageContract` with a dedicated
  `view_kind` (e.g. `"grid"`) and a caption per `TASK-174`, so the VLM is told it
  is a multi-view montage rather than a single render
- grid composition is deterministic and reversible (it only reads written capture
  files; it does not mutate scene state)

## Implementation Notes

- The selected captures already exist as written JPEG files referenced by
  `VisionCaptureImageContract.image_path` from
  `capture_stage_images` (`capture_runtime.py:241-258`). A grid composite is a
  pure post-capture, file-level operation: read the selected cell images, tile
  them into one labeled montage, write it via the same
  `get_viewport_output_paths` helper used at `capture_runtime.py:243-247`, and
  emit one more `VisionCaptureImageContract` for the montage. No scene/viewport
  manipulation is involved, so `capture_scene_state` / `restore_scene_state`
  (`:265-319`) are not needed for the compositing step itself.
- Placement in the pipeline: the grid is built *after* budget-aware selection
  (`TASK-177-01`) so it composites exactly the views that would otherwise be
  transmitted. When the grid flag is on, the request should transmit the single
  montage in place of the individual cells (or alongside a small reserved set),
  and `build_vision_request_from_capture_bundle` /
  `build_vision_request_from_stage_captures` in
  `server/adapters/mcp/vision/capture.py:33-88` consume the montage like any
  other capture via `_capture_to_image_input` (`:20-30`).
- Config flag: add `VISION_CAPTURE_GRID_ENABLED` (default `False`) to
  `server/infrastructure/config.py` next to the other `VISION_*` keys
  (`:52-79`), surface it on `VisionRuntimeConfig`
  (`server/adapters/mcp/vision/config.py:113-130`) as an additive boolean field,
  and keep it default-off so no behavior changes unless explicitly enabled.
- Contract: extend `VisionCaptureImageContract.view_kind`
  (`server/adapters/mcp/contracts/vision.py:22`) with `"grid"` (additive,
  alongside the `TASK-177-02` `"top"`/`"oblique"` additions). The montage cell
  labels are baked into the image pixels (IG-VLM style) and the per-image caption
  is provided through the `TASK-174` caption seam, so the VLM is explicitly told
  it is looking at a labeled multi-view grid.
- Image library: prefer a dependency already present in the project for tiling
  (e.g. Pillow if available) rather than adding a heavy new dependency; the
  composite is plain raster tiling + text labels and must stay default-off so it
  never becomes a required runtime cost. This is not a perception sidecar and
  must not reopen the `TASK-172` / `TASK-140-06` optional-runtime substrate.
- Research basis (cite by name + arXiv id): **IG-VLM (arXiv:2403.18406)** shows
  that arranging multiple frames into a single labeled image grid lets a single
  VLM call reason across views and can outperform passing many separate images,
  which is exactly the budget/model regime this flag targets. Treat the reported
  gains as video-QA evidence and re-measure on `tests/fixtures/vision_eval`
  before promoting the grid path past default-off.

## Pseudocode

```python
def maybe_build_view_grid(selected_captures, *, runtime, bundle_id, stage):
    if not runtime.capture_grid_enabled:          # default-off flag
        return selected_captures, None
    cells = [read_image(c.image_path) for c in selected_captures]
    labels = [c.preset_name or c.label for c in selected_captures]
    montage = tile_with_labels(cells, labels)     # deterministic rows x cols
    filename = f"{bundle_id}_{stage}_view_grid.jpg"
    internal_file, _il, external_file, _el = get_viewport_output_paths(filename)
    write_jpeg(internal_file, montage)
    grid_capture = VisionCaptureImageContract(
        label=f"view_grid_{stage}",
        image_path=str(internal_file),
        host_visible_path=external_file,
        preset_name="view_grid",
        media_type="image/jpeg",
        view_kind="grid",                          # caption supplied via TASK-174
    )
    # Transmit the montage in place of the individual cells (budget-aware).
    return [grid_capture], grid_capture
```

## Runtime / Security Contract Notes

- The grid is advisory VLM-facing input only; the in-image cell labels and the
  TASK-174 caption are interpretation context, not scene truth. Keep
  `not_truth_source` / `requires_deterministic_checks_for_correctness`. The grid
  must not gate or unlock tools and must not be treated as a measurement source.
- Default-off: with `VISION_CAPTURE_GRID_ENABLED=False` the bundle is byte-for-byte
  the current per-image behavior. The flag is a transmission-shape choice, not a
  new capability tier, and does not reopen the TASK-172 optional-runtime seam.
- Bounded budget: the montage ships as one transmitted image and must never push
  the request past the runner image-budget guard (`runner.py:170-179`); compose
  after selection so the grid only contains already-budgeted views.
- Do not emit raw coordinate tokens; cell labels are symbolic view-kind /
  preset-name strings. Any proportion the grid helps the VLM perceive remains a
  proportional ratio vs a trusted reference anchor, never an authoritative
  absolute measurement.

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_capture_runtime.py`
- `tests/unit/adapters/mcp/test_vision_capture_bundle.py`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/MULTI_VIEW_CAPTURE_PLAN.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`

## Changelog Impact

- add/update one `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- board tracking remains on umbrella `TASK-177`
- no separate promoted board-row change is expected for this subtask unless it
  later becomes a standalone follow-on

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_capture_runtime.py tests/unit/adapters/mcp/test_vision_capture_bundle.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Validation Category

- optional labeled multi-view grid composite proof
