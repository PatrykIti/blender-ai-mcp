# TASK-176-01: Capture-Ok And Warning Signals For Capture Bundles

**Parent:** [TASK-176](./TASK-176_Capture_Failure_And_Evidence_Truncation_Signal_Surfacing.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Follow-on After:** [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md)
**Objective:** Detect when an addon camera/view operation returned an error string instead of succeeding and propagate `capture_ok=False` / `capture_warning` onto the per-image contract plus a bundle-level `capture_warnings` list, so a mislabeled or failed view never reaches the VLM as trustworthy evidence.
**Repository Touchpoints:** `server/adapters/mcp/vision/capture_runtime.py`, `server/adapters/mcp/contracts/vision.py`, `blender_addon/application/handlers/scene_viewport_mixin.py`, `tests/unit/adapters/mcp/test_vision_capture_runtime.py`, `tests/unit/adapters/mcp/test_vision_capture_bundle.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/e2e/vision/test_reference_understanding_runtime_surface.py`
**Acceptance Criteria:**
- a camera/view operation (`isolate_object`, `set_standard_view`, `camera_focus`, `camera_orbit`) that returns a non-`None`, non-empty string is treated as a failed step for that preset, not as success
- the resulting `VisionCaptureImageContract` carries `capture_ok=False` and a bounded `capture_warning` naming which operation failed and the preset/view it was meant to produce; a successful capture carries `capture_ok=True` and no `capture_warning`
- `build_capture_bundle(...)` produces a bundle-level `capture_warnings` list summarizing each failed per-image capture for the stage; an all-clean stage yields an empty list
- the additive contract fields default to a reliability-neutral value (`capture_ok=True`, `capture_warning=None`, `capture_warnings=[]`) so existing serialized payloads and tests stay valid
- the `except Exception: pass` blocks (capture_runtime.py:211/216/221/232) still swallow genuine exceptions for reversibility, but a returned error string is now recorded instead of discarded
- no new field unlocks a tool, marks a gate complete, or asserts scene truth; the signal is purely advisory reliability metadata

## Implementation Notes

- The verified gap is in `capture_stage_images`
  (`server/adapters/mcp/vision/capture_runtime.py:186-262`). Each viewport
  operation is wrapped in `try: ... except Exception: pass` at lines 209-211
  (`isolate_object`), 213-216 (`set_standard_view`), 218-222 (`camera_focus`),
  and 224-233 (`camera_orbit`). The handlers' return values are discarded, then
  the contract is appended unconditionally at lines 249-258 with
  `label=f"{preset.name}_{stage}"` and `preset_name=preset.name`.
- The addon proves these handlers return strings on the common headless failure:
  `set_standard_view` returns
  `"No 3D viewport found. Standard view requires an active 3D view."`
  (`blender_addon/application/handlers/scene_viewport_mixin.py:1100`),
  `camera_focus` returns the matching focus message (line 364), and
  `camera_orbit` returns the matching orbit message (line 323). On success they
  return human-readable confirmation strings (`"Set 3D viewport to FRONT view"`,
  `"Focused on '<name>' ..."`, `"Orbited viewport by ..."`).
- A returned string is ambiguous between "success confirmation" and "failure
  message", so detection must be conservative and deterministic. Treat a return
  value as a failure only when it matches a bounded set of known failure
  prefixes/markers (for example a normalized `"no 3d viewport found"` substring),
  not merely "is a non-empty string". This avoids regressing the common case
  where success confirmations are also strings, and keeps the addon contract the
  source of the failure vocabulary. A small `_classify_view_op_result(...)`
  helper in `capture_runtime.py` should own this classification so it is unit
  testable and so adding a new handler failure phrase is a one-line change.
- Per the advisory boundary, `capture_ok=False` does not abort the bundle by
  default. The contract still carries the image path so deterministic checks can
  inspect it, but the reliability annotation lets policy/orchestration
  down-weight or skip it. This is the missing trust signal behind the squirrel
  mislabeled-view failure class.
- Keep both RPC sides aligned: the addon handlers already return these strings,
  so no addon behavior change is required for the common case; if a follow-up
  decides to make the addon return a structured `{ "ok": false, "reason": ... }`
  envelope, that is an additive RPC change that must update both the addon
  handler and the server-side reader plus tests, and remain main-thread-safe and
  reversible via `capture_scene_state` / `restore_scene_state`.
- Research basis (cite by name + arXiv id): DiffuRank (arXiv:2404.07984) shows
  that ambiguous or non-canonical views drive multimodal hallucination, which is
  exactly what a silently mislabeled `target_top` capture induces; 3DSRBench
  (arXiv:2412.07825) documents how brittle VLM spatial reasoning is to viewpoint
  changes, motivating an explicit per-image reliability flag; LL3M
  (arXiv:2508.08228) frames a Critic/Verify reliability layer where the system
  must surface when its own perception step is unreliable rather than emitting a
  confident-looking result.

## Pseudocode

```python
# capture_runtime.py
_KNOWN_VIEW_OP_FAILURE_MARKERS = ("no 3d viewport found",)


def _classify_view_op_result(result) -> str | None:
    """Return a bounded warning string when a handler reported failure, else None."""
    if result is None:
        return None
    text = str(result).strip()
    if not text:
        return None
    normalized = text.lower()
    if any(marker in normalized for marker in _KNOWN_VIEW_OP_FAILURE_MARKERS):
        return text[:240]
    return None


# inside capture_stage_images, per preset:
warnings: list[str] = []

if preset.standard_view and hasattr(scene_handler, "set_standard_view"):
    try:
        result = scene_handler.set_standard_view(preset.standard_view)
    except Exception:
        result = None  # genuine exception still swallowed for reversibility
    warning = _classify_view_op_result(result)
    if warning is not None:
        warnings.append(f"set_standard_view({preset.standard_view}): {warning}")

# ... same pattern for isolate_object / camera_focus / camera_orbit ...

capture_ok = not warnings
capture_warning = "; ".join(warnings)[:240] if warnings else None
captures.append(
    VisionCaptureImageContract(
        label=f"{preset.name}_{stage}",
        image_path=str(internal_file),
        host_visible_path=external_file,
        preset_name=preset.name,
        media_type="image/jpeg",
        view_kind=preset.view_kind,
        capture_ok=capture_ok,
        capture_warning=capture_warning,
    )
)


# build_capture_bundle(...): aggregate the per-image warnings
def _collect_capture_warnings(*image_lists) -> list[str]:
    collected: list[str] = []
    for images in image_lists:
        for image in images:
            if not image.capture_ok and image.capture_warning:
                collected.append(f"{image.label}: {image.capture_warning}")
    return collected
# pass capture_warnings=_collect_capture_warnings(captures_before, captures_after)
# into VisionCaptureBundleContract(...)
```

## Runtime / Security Contract Notes

- Vision stays advisory. `capture_ok` / `capture_warning` / `capture_warnings`
  are reliability metadata about the deterministic capture step; they are
  `not_truth_source` and `requires_deterministic_checks_for_correctness`. They
  must not mark a gate complete or unlock a tool.
- The capture path stays main-thread-safe and reversible: the existing
  `capture_scene_state` / `restore_scene_state` flow and the `finally` restore in
  `capture_stage_images` are unchanged. Detecting a returned error string adds no
  new Blender mutation.
- No magnitudes and no raw coordinate tokens are introduced; the new fields are a
  boolean plus bounded symbolic strings only.
- Detection is fail-safe biased toward not under-reporting: when a handler return
  is ambiguous, prefer flagging a known failure marker over silently trusting it,
  but never flag a clean success confirmation as a failure.

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_capture_runtime.py` (extend the existing
  fake handler so `set_standard_view` / `camera_focus` / `camera_orbit` can
  return the `"No 3D viewport found..."` strings, and assert `capture_ok=False`
  plus a populated `capture_warning` on the affected preset while clean presets
  stay `capture_ok=True`)
- `tests/unit/adapters/mcp/test_vision_capture_bundle.py` (assert
  `build_capture_bundle(...)` aggregates `capture_warnings` from failed images
  and yields an empty list for an all-clean stage)
- `tests/unit/adapters/mcp/test_reference_images.py` (assert the reliability
  annotation survives into the reference/orchestrator-facing projection)
- `tests/e2e/vision/test_reference_understanding_runtime_surface.py` (prove the
  capture-warning surface is observable end to end without changing gate
  authority)

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- board tracking remains on umbrella `TASK-176`
- no separate promoted board-row change is expected for this subtask unless it
  later becomes a standalone follow-on

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_capture_runtime.py tests/unit/adapters/mcp/test_vision_capture_bundle.py tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`

## Validation Category

- capture-reliability signal-surfacing proof
