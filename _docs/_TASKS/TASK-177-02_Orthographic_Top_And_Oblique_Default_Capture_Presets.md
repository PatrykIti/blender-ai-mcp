# TASK-177-02: Orthographic Top And Oblique Default Capture Presets

**Parent:** [TASK-177](./TASK-177_Reachable_Rich_Multi_View_Capture_And_Top_View_Default.md)
**Status:** ✅ Done
**Priority:** 🟡 Medium
**Follow-on After:** [TASK-177-01](./TASK-177-01_Decouple_Capture_From_Transmission_And_Budget_Aware_Selection.md)
**Objective:** Make an orthographic top/overhead view a first-class, always-present member of the default capture bundle, add an oblique 3/4 view when the budget allows, cap the transmitted set at roughly 6-8 views, and record per-view projection / view-kind metadata so the downstream VLM knows what each view actually is without parsing coordinates.
**Repository Touchpoints:** `server/adapters/mcp/vision/capture_runtime.py`, `server/adapters/mcp/contracts/vision.py`, `blender_addon/application/handlers/scene_viewport_mixin.py`, `tests/unit/adapters/mcp/test_vision_capture_runtime.py`, `tests/unit/adapters/mcp/test_vision_capture_bundle.py`, `tests/e2e/vision/test_real_view_variant_model_comparison.py`
**Acceptance Criteria:**
- the default compact bundle guarantees an orthographic top/overhead view
  (`target_top`, `standard_view="TOP"`) as a retained member, not an optional
  extra that selection can drop first
- an oblique 3/4 view (using `camera_orbit`, e.g. the existing
  `orbit_horizontal=-35.0, orbit_vertical=15.0` shape) is added to the default
  candidate set and retained when the transmit budget allows
- the transmitted set is capped at roughly 6-8 views, consistent with the
  budget-aware selection from `TASK-177-01`
- each capture records deterministic projection / view-kind metadata
  (orthographic-top vs perspective-oblique vs wide vs focus) on
  `VisionCaptureImageContract` so the VLM and orchestrator can distinguish view
  kinds symbolically
- top and oblique capture remain reversible via `capture_scene_state` /
  `restore_scene_state` and the existing addon view-state restore path

## Implementation Notes

- The compact preset set in `capture_runtime.py:48-87`
  (`COMPACT_CAPTURE_PRESET_SPECS`) already includes a `target_top` spec with
  `standard_view="TOP"`, but `view_kind` is the generic `"focus"` and there is no
  oblique view in the compact set. The rich set
  (`RICH_CAPTURE_PRESET_SPECS`, `:89-170`) has obliques
  (`target_oblique_left` / `target_oblique_right`, `:107-128`) but is unreachable
  by default (see `TASK-177-01`). This subtask brings the high-value top + one
  oblique into the *default* transmitted set.
- The addon already supports the needed reversible atomics on
  `blender_addon/application/handlers/scene_viewport_mixin.py`:
  `set_standard_view(view_name)` accepts `FRONT|RIGHT|TOP` (`:1081-1105`),
  `camera_orbit(...)` (`:296-342`) applies a reversible viewport rotation, and
  `get_view_state` / `restore_view_state` (`:1006-1079`) back the
  capture-state restore in `capture_runtime.restore_scene_state` (`:301-319`).
  No new persistent camera rig is needed; keep the reversible viewport path per
  `_docs/_VISION/MULTI_VIEW_CAPTURE_PLAN.md`.
- View-kind metadata: `VisionCaptureImageContract.view_kind`
  (`server/adapters/mcp/contracts/vision.py:22`) is currently
  `Literal["wide", "focus", "overlay", "reference"]`, and the capture loop sets
  `view_kind=preset.view_kind` (`capture_runtime.py:256`) where
  `CapturePresetSpec.view_kind` is `Literal["wide", "focus"]`
  (`capture_runtime.py:37`). To let the VLM tell an orthographic overhead apart
  from an oblique, extend both literals with view kinds such as `"top"` and
  `"oblique"` (additive; keep the existing values so
  `infer_capture_preset_profile` / `choose_reference_target_view` in `policy.py`
  and existing tests stay valid). A `projection` hint
  (orthographic vs perspective) can be carried either as a dedicated optional
  field on the contract or folded into `view_kind`; prefer a small additive field
  so it stays symbolic and does not become a coordinate dump.
- The capture loop in `capture_stage_images` (`:204-258`) already swallows
  camera-op failures with `except Exception: pass` (`:211/216/221/232`). Adding
  the top + oblique presets to the default candidate set does not change that
  control flow; the orthographic top uses the `standard_view` branch (`:213`) and
  the oblique uses the `camera_orbit` branch (`:224-233`). Keep both reversible:
  the loop already calls `restore_scene_state(scene_handler, original_state)`
  between presets (`:206-207`) and in `finally` (`:259-260`).
- The capture label format `f"{preset.name}_{stage}"` (`:251`) and
  `preset_name=preset.name` (`:254`) keep selection/labeling deterministic, so
  the new presets remain compatible with `TASK-177-01` budget-aware selection
  and with per-image captioning (see `TASK-174` below).
- Research basis (cite by name + arXiv id): **VSI-Bench (arXiv:2412.14171)**
  shows top-down/overhead map views materially help relative-distance and spatial
  reasoning (~+20-32% in that benchmark), motivating top-view as a default rather
  than an optional extra. **GPT4Scene (arXiv:2501.01428)** uses a bird's-eye-view
  representation to ground multi-view understanding, reinforcing the overhead
  view's value. **Orient Anything (arXiv:2412.18605)** motivates including
  canonical orthographic views (front/side/top) so orientation is unambiguous.
  These are indoor-scan / synthetic studies; re-measure on
  `tests/fixtures/vision_eval` before promotion.

## Pseudocode

```python
# Additive view kinds so the VLM can distinguish projections symbolically.
# contracts/vision.py: VisionCaptureImageContract.view_kind
#   Literal["wide", "focus", "overlay", "reference", "top", "oblique"]
# capture_runtime.py: CapturePresetSpec.view_kind
#   Literal["wide", "focus", "top", "oblique"]

DEFAULT_TOP_PRESET = CapturePresetSpec(
    name="target_top",
    standard_view="TOP",
    focus_target=True,
    isolate_target=True,
    view_kind="top",            # orthographic overhead, retained early in selection
)

DEFAULT_OBLIQUE_PRESET = CapturePresetSpec(
    name="target_oblique_left",
    focus_target=True,
    isolate_target=True,
    orbit_horizontal=-35.0,
    orbit_vertical=15.0,
    view_kind="oblique",        # perspective 3/4, retained when budget allows
)

# Selection (TASK-177-01) ranks context_wide and target_top above oblique/detail,
# so the orthographic overhead survives the 6-8 view cap; the oblique survives
# only when transmit_budget leaves room.
```

## Runtime / Security Contract Notes

- Top and oblique captures are still advisory VLM-facing inputs; view-kind /
  projection metadata is interpretation context, not scene truth. Keep
  `not_truth_source` / `requires_deterministic_checks_for_correctness`. Capture
  view kinds must not gate or unlock tools.
- All addon-side view manipulation stays main-thread-safe and reversible via
  `capture_scene_state` / `restore_scene_state` and the addon
  `get_view_state` / `restore_view_state` path; no persistent camera objects are
  added to the user scene.
- Both RPC sides stay in sync: the server-side `CapturePresetSpec` / contract and
  the addon `SceneViewportMixin` atomics must agree on `TOP` and orbit semantics,
  and tests cover both.
- Any proportion or distance the overhead view later helps infer is a
  proportional ratio vs a trusted reference anchor, never an authoritative
  absolute measurement; do not emit raw coordinate tokens as primary evidence.

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_capture_runtime.py`
- `tests/unit/adapters/mcp/test_vision_capture_bundle.py`
- `tests/e2e/vision/test_real_view_variant_model_comparison.py`

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
- 2026-05-31: completed. Compact staged capture now includes `target_top` as an
  orthographic top view and `target_oblique_left` as a perspective oblique view;
  rich presets carry the same symbolic `view_kind` / `projection` metadata.
  Focus/top/oblique overlays remain compatible with the default-off Set-of-Mark
  path.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_capture_runtime.py tests/unit/adapters/mcp/test_vision_capture_bundle.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
- 2026-05-31 focused validation:
  `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_capture_runtime.py tests/unit/adapters/mcp/test_vision_capture_bundle.py tests/unit/adapters/mcp/test_vision_policy.py -q` -> 37 passed
  `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_capture_runtime.py tests/unit/adapters/mcp/test_vision_capture_bundle.py tests/unit/adapters/mcp/test_vision_silhouette.py tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_reference_images.py::test_reference_orchestrator_feedback_projects_runtime_policy_block tests/unit/adapters/mcp/test_reference_images.py::test_reference_orchestrator_feedback_tags_authoritative_next_action_provenance tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_vision_prompting.py -q` -> 180 passed

## Validation Category

- multi-view preset coverage and reversible viewport-capture proof
