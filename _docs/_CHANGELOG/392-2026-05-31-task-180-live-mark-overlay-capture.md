# 392 - TASK-180-01 live Set-of-Mark overlay capture

Date: 2026-05-31

## Summary

Shipped the default-off live Set-of-Mark overlay capture path for staged
reference compare. Focus presets can now append a supplemental
`view_kind="overlay"` image built from deterministic isolate-per-object renders,
with a typed mark-id map back to scene objects.

## Changes

- Added `VISION_MARK_OVERLAY_ENABLED=false` and threaded it through runtime
  vision config.
- Added `VisionOverlayMarkContract` and `VisionCaptureImageContract.overlay_marks`.
- Added runtime overlay capture emission in `capture_stage_images(...)` for
  selected focus presets, using existing reversible viewport/isolation helpers.
- Kept overlay captures supplemental: they stay outside grid composites and drop
  before primary focus/context captures under packet image-budget pressure.
- Serialized placed overlay mark legends into packet payloads so VLM findings
  can refer only to visible symbolic mark ids.
- Preserved stable sorted mark numbering even when some objects are unmarked.
- Hardened `USER_PERSPECTIVE` depth/normal E2E coverage to include edit-mode and
  multi-object selection restoration.
- Added E2E coverage for real Blender object-set overlay capture and visibility
  restoration.

## Validation

- `poetry run ruff check ...`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_capture_runtime.py tests/unit/adapters/mcp/test_vision_capture_bundle.py tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_vision_marks.py -q`
- `PYTEST_ADDOPTS='-k "depth_pass_supports_user_perspective_view or normal_pass_supports_user_perspective_view or set_of_mark_overlay"' poetry run python scripts/run_e2e_tests.py`
