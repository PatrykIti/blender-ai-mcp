# 370. TASK-176 capture-failure and evidence-truncation signal surfacing

Date: 2026-05-30

## Summary

Implemented `TASK-176`: the bounded capture/parse path now surfaces, instead of
swallowing, two classes of silent failure. Camera/view operations that return a
known failure marker string (headless Blender returns these instead of raising)
are now recorded on the capture contract rather than discarded, so a mislabeled
view no longer reaches the VLM as trustworthy. And the parse path now reports
when finding lists were truncated and distinguishes a genuine "scene looks
correct" empty result from a recovery placeholder. All additive fields with
reliability-neutral defaults.

## Changes

- `server/adapters/mcp/contracts/vision.py`: added `capture_ok: bool = True` and
  `capture_warning: str | None` to `VisionCaptureImageContract`, plus a
  bundle-level `capture_warnings: list[str]` on `VisionCaptureBundleContract`.
- `server/adapters/mcp/vision/capture_runtime.py`: added
  `_classify_view_op_result` with a bounded `_KNOWN_VIEW_OP_FAILURE_MARKERS` set;
  `capture_stage_images` now captures each `isolate_object` / `set_standard_view`
  / `camera_focus` / `camera_orbit` return value (and any raised exception),
  classifies it, and records `capture_ok=False` + a `capture_warning` on the
  affected capture without aborting the bundle; `build_capture_bundle` aggregates
  the per-image warnings. Success-confirmation strings are intentionally not
  treated as failures.
- `server/adapters/mcp/sampling/result_types.py`: added `evidence_truncated`,
  `omitted_count`, and `analysis_unusable` to `VisionAssistContract`, each with a
  description.
- `server/adapters/mcp/vision/parsing.py`: added `_bounded_string_list_counted`
  (returns the bounded list plus dropped count); the compare builder now sums the
  omitted items across the five capped finding lists and emits
  `evidence_truncated`/`omitted_count`; the input-echo, label-map, and
  off-contract recovery payloads now set `analysis_unusable=True` so their empty
  finding lists are not misread as a clean scene.

## Tests

- `tests/unit/adapters/mcp/test_vision_capture_runtime.py`: success strings keep
  `capture_ok=True`; a failure-marker `set_standard_view` flags `capture_ok=False`
  with a warning without aborting; `build_capture_bundle` aggregates warnings
- `tests/unit/adapters/mcp/test_vision_parsing.py`: echo payload is
  `analysis_unusable`; over-cap evidence sets `evidence_truncated` with an
  `omitted_count`; within-cap evidence is not truncated
- `ruff` and `mypy` clean on the touched modules

## Research Basis

DiffuRank (arXiv:2404.07984) and 3DSRBench (arXiv:2412.07825): ambiguous /
mislabeled views drive VLM hallucination, so surfacing capture reliability and
truncation prevents the loop from trusting degraded evidence. LL3M
(arXiv:2508.08228) motivates distinguishing "verified clean" from "could not
evaluate". Re-measure on `tests/fixtures/vision_eval` before claiming gains.
