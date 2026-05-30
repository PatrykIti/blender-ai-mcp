# 380. TASK-183-02 silhouette calibration and IoU convergence signal

Date: 2026-05-30

## Summary

Implemented the deterministic-calibration core of `TASK-183-02`: removed the dead
silhouette band metrics, normalized `aspect_ratio_delta` onto the band/IoU
severity scale, and added a deterministic IoU convergence signal so the loop has a
monotonic "closer / further / stalled than last cycle" verdict.

## Changes

- `server/adapters/mcp/vision/silhouette.py`:
  - dropped `mid_band_width_delta` and `lower_band_width_delta` — they were
    computed every cycle but never consumed by
    `build_action_hints_from_silhouette` (the consumer uses `mask_iou`,
    `upper_band_width_delta`, `left_projection_delta`, `right_projection_delta`)
  - normalized `aspect_ratio_delta` to a relative fraction of the reference aspect
    ratio so its severity bands (`0.35`/`0.18`) are comparable to the
    `[0, 1]`-scaled band/IoU metrics, instead of an unbounded raw ratio difference
  - added `compute_iou_convergence(previous_iou, current_iou)` returning an
    advisory `improved` / `regressed` / `stalled` / `unknown` verdict with the IoU
    delta, giving the loop a deterministic convergence/stop signal

## Tests

- `tests/unit/adapters/mcp/test_vision_silhouette.py`: convergence classification
  + unavailable handling; the dead band metrics are no longer emitted while the
  consumed metrics remain; `aspect_ratio_delta` is a normalized relative fraction
  with calibrated severity
- consumer (`reference_silhouette`) tests stay green; `ruff`/`mypy` clean; full
  `tests/unit` green

## Follow-on

The heavy render-vs-reference embedding cross-check variant (MEt3R / DINO-style),
which `TASK-183-02` also scopes, stays behind the default-off sidecar seam and is
not added here. Wiring `compute_iou_convergence` into the live iterate loop as a
surfaced stop signal is a small follow-up.

## Research Basis

IR3D-Bench (arXiv:2506.23329) deterministic-first metrics; MEt3R
(arXiv:2501.06336) consistency scoring. Calibrate against
`tests/fixtures/vision_eval` before claiming gains.
