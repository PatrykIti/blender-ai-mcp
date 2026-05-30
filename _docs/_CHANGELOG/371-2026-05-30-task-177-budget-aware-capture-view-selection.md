# 371. TASK-177 budget-aware capture view selection

Date: 2026-05-30

## Summary

Implemented the core of `TASK-177` (subtask `TASK-177-01`): decouple capture
from transmission with a deterministic best-N view selector, so a richer capture
set can be down-selected to fit the image budget instead of having the whole
request hard-rejected as over-budget. This is the reusable substrate that makes
the richer multi-view capture path reachable.

## Changes

- `server/adapters/mcp/vision/capture.py`: added
  `select_capture_views_within_budget`, ranking captures by a canonical
  informativeness priority (orthographic triad front/side/top first, then an
  oblique 3/4 that best reveals 3D form, then context wide, then focus/detail),
  tie-broken by original order and re-emitted in original order so the
  roster/caption ordering stays stable.
- both request builders (`build_vision_request_from_stage_captures`,
  `build_vision_request_from_capture_bundle`) now accept an optional
  `max_images`; when set they down-select the stage/before/after captures to fit
  the budget after reserving room for the reference images. Default `None` keeps
  the existing behaviour, so the change is fully backward compatible.
- `server/adapters/mcp/vision/integration.py`: the macro before/after bundle flow
  now passes `effective_max_images`, so it degrades gracefully instead of risking
  an over-budget rejection. (The staged packet compare path already trims per
  packet and is left unchanged.)
- exported `select_capture_views_within_budget` from the vision package.

## Tests

- `tests/unit/adapters/mcp/test_vision_capture_bundle.py`: the selector keeps the
  orthographic triad first, is a no-op within budget, and the stage builder
  down-selects to budget while reserving reference slots; no-budget calls are
  unchanged
- `ruff` and `mypy` clean on the touched modules

## Follow-on

- `TASK-177-02` (add the oblique 3/4 view to the default compact preset) and
  `TASK-177-03` (optional labelled multi-view grid composite) remain open; the
  compact set already includes the orthographic top view, and the selector above
  now makes adding the oblique budget-safe.

## Research Basis

DiffuRank (arXiv:2404.07984): a few well-chosen views beat many; VSI-Bench
(arXiv:2412.14171) and GPT4Scene (arXiv:2501.01428): canonical/overhead views aid
spatial reasoning. Re-measure on `tests/fixtures/vision_eval` before claiming
gains.
