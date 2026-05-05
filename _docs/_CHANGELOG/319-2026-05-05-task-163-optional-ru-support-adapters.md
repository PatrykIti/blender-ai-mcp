# 319. TASK-163 optional RU support adapters

Implemented the `TASK-163-05` and `TASK-163-06` optional support-adapter wave
on the existing reference-understanding seams.

## What Changed

- added a typed default-off `reference_classifier` runtime/config seam through:
  - `VISION_REFERENCE_CLASSIFIER_*`
  - `VisionReferenceClassifierConfig`
  - `VisionRuntimeConfig.reference_classifier`
- classifier config can now inherit endpoint/provider credentials from the main
  external vision runtime, while still allowing a classifier-specific model or
  a full sidecar-specific override set
- kept the existing `VISION_SEGMENTATION_*` seam as the owner for RU-side
  optional segmentation linkage instead of introducing a second registry
- RU refresh can now optionally call explicit support-only sidecars and merge:
  - `classification_scores`
  - `segmentation_artifacts`
- optional adapter failures or empty results now degrade to bounded provenance
  notes and empty support-evidence lists instead of breaking guided sessions
- compact `reference_orchestrator_feedback` now summarizes optional classifier
  and segmentation support evidence on the existing `reference_images(...)`,
  `router_*`, and staged checkpoint surfaces
- updated `TASK-163-05` and `TASK-163-06` to `✅ Done`; `TASK-163-07` remains
  open for live-backend closeout

## Validation

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_reference_images.py -q`
