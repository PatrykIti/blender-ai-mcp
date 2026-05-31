# 390. TASK-179 live object-ID sidecar IoU

Date: 2026-05-31

## Summary

Wired the TASK-179 per-object IoU substrate into the staged compare runtime
without completing the broader auxiliary-image transmission lane. Staged compare
now captures an internal object-ID sidecar for the canonical focus view, uses it
to populate capture-side `per_object_metrics`, and keeps that sidecar out of the
VLM image roster until TASK-179-03 finishes captions and budget reporting.

## Changes

- Added `VisionObjectIdCaptureArtifactContract` and attached it optionally to
  `VisionCaptureImageContract` as an internal sidecar rather than a transmitted
  VLM image.
- Updated `capture_stage_images(...)` to optionally request one
  `scene.get_object_id_pass(camera_name="USER_PERSPECTIVE")` sidecar for the
  target focus preset, write the PNG through the viewport-output path helper,
  and preserve primary viewport captures on sidecar failure.
- Updated the Blender addon object-ID pass so `USER_PERSPECTIVE` mirrors the
  active 3D viewport into a temporary camera and restores the temporary camera,
  selection, active object, render settings, compositor state, object mode, and
  object `pass_index` values.
- Extended silhouette analysis to build capture-side per-object IoU metrics from
  the sidecar `index_map` and object-ID PNG, including typed unavailable metrics
  when the pass or part is absent.
- Threaded per-object metrics through stage-level and packet-level staged
  compare support evidence with explicit capture-side advisory wording.
- Left TASK-179-02 open for fixture-calibrated per-object severity thresholds
  and TASK-179-03 open for depth/normal/object-ID auxiliary transmission,
  captions, budget-drop reporting, and external payload proof.

## Tests

Focused validation run during implementation:

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_capture_runtime.py tests/unit/adapters/mcp/test_vision_capture_bundle.py tests/unit/adapters/mcp/test_vision_silhouette.py -q` (41 passed)
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_capture_runtime.py tests/unit/adapters/mcp/test_vision_capture_bundle.py tests/unit/adapters/mcp/test_vision_silhouette.py tests/unit/addon/test_addon_registration.py -q` (44 passed)
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py -q` (24 passed)
- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_viewport_control.py -q` (11 passed)
- `PYTEST_ADDOPTS='-k test_object_id_pass_supports_user_perspective_view' poetry run python scripts/run_e2e_tests.py` (1 passed, 496 deselected)
- `poetry run mypy` (success: no issues found in 758 source files)
- `PYTHONPATH=. poetry run pytest ./tests/unit` (3586 passed)
- `poetry run python scripts/run_e2e_tests.py` (492 passed, 5 skipped; log:
  `tests/e2e/e2e_test_PASSED_20260531_021456.log`)
- `git diff --check` (passed)
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure` (passed after
  `ruff-format` normalized one file on the first run)
