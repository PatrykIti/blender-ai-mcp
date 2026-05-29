# TASK-183-02: Deterministic Cross-Check And Silhouette Threshold Calibration

**Parent:** [TASK-183](./TASK-183_Capability_Enriched_Vision_Schema_And_Deterministic_Cross_Check.md)
**Status:** ⏳ To Do
**Priority:** 🟡 Medium
**Follow-on After:** [TASK-166-03-01](./TASK-166-03-01_Always_On_Heuristic_CV_Metrics.md), [TASK-172-04](./TASK-172-04_SAM_Or_SAM2_Local_Mask_And_Landmark_Support.md)
**Objective:** Add a deterministic render-vs-reference consistency score (lightweight always-on variant plus an optional default-off heavy embedding variant) that flags VLM-vs-geometry disagreement, down-weights unverified visual claims, and acts as a monotonic convergence/stop signal across iterations; and calibrate the silhouette severity thresholds against a golden fixture with a regression test, rescale `aspect_ratio_delta` onto the band/IoU scale, and either wire up or remove the dead `mid_band`/`lower_band` metrics.
**Repository Touchpoints:** `server/adapters/mcp/vision/silhouette.py`, `server/adapters/mcp/areas/reference_silhouette.py`, `server/adapters/mcp/vision/evaluation.py`, `server/adapters/mcp/vision/config.py`, `server/adapters/mcp/contracts/reference.py`, `tests/unit/adapters/mcp/test_vision_silhouette.py`, `tests/unit/adapters/mcp/test_vision_evaluation.py`, `tests/e2e/vision/test_reference_stage_silhouette_contract.py`, `tests/fixtures/vision_eval/`

**Acceptance Criteria:**
- silhouette severity thresholds in `vision/silhouette.py` are calibrated against a repo-owned golden fixture (under `tests/fixtures/vision_eval/`) and defended by a regression test, replacing the current magic-number constants (`mask_iou` `high=0.35`/`medium=0.18` at `:256`, etc.)
- `mask_iou` no longer assumes an unattainable `reference_value=1.0` ideal across mismatched views; severity is computed against a calibrated achievable band rather than distance from a perfect-overlap fiction
- `aspect_ratio_delta` (`:266-271`) is normalized onto a band/IoU-comparable scale so its `high`/`medium` thresholds mean the same thing as the other normalized metrics
- `mid_band_width_delta` and `lower_band_width_delta` (`:276-277`) are either consumed by an action hint in `areas/reference_silhouette.py` / projected as compare support evidence, or removed; no metric is computed and silently dropped
- a deterministic render-vs-reference consistency score is produced each cycle, exposed as advisory evidence, and used to down-weight unverified VLM visual claims and to provide a monotonic "closer than last cycle" convergence/stop signal
- the heavy embedding variant (CLIP/DINO/MEt3R-DUSt3R-style) stays **default-off**, advisory-only, and packet-bounded behind the existing `TASK-172` optional-runtime seam; the lightweight deterministic variant carries no new heavy dependency
- the consistency score and silhouette metrics keep `not_truth_source` / `requires_deterministic_checks_for_correctness`; they do not pass gates or unlock tools

## Implementation Notes

- `build_silhouette_analysis` (`vision/silhouette.py:190`) already produces a
  normalized bbox-aligned mask pair (`_normalize_mask` -> 128x128 at
  `vision/silhouette.py:169`) and computes `mask_iou`, `contour_drift`,
  `aspect_ratio_delta`, plus five band metrics. The severity helper
  `_metric_severity` (`vision/silhouette.py:17`) takes raw `high`/`medium`
  magic numbers per metric. The calibration must derive those thresholds from
  fixtures instead of hardcoding them.
- The `mask_iou` metric is scored as `delta = (intersection/union) - 1.0` against
  a fixed `reference_value=1.0` (`vision/silhouette.py:253-256`). A perfect IoU is
  unattainable across mismatched reference/capture views, so "distance from 1.0"
  conflates view mismatch with shape error. Recalibrate against an achievable
  IoU band measured on golden fixtures (e.g. the matching-shape fixtures already
  proven in `test_vision_silhouette.py:48` show IoU > 0.98 for aligned shapes;
  mismatched golden pairs give the realistic ceiling).
- `aspect_ratio_delta` (`vision/silhouette.py:266-271`) is an unnormalized ratio
  difference (`capture_aspect_ratio - reference_aspect_ratio`) but reuses the
  same `high=0.35`/`medium=0.18` band as `mask_iou`. Normalize it (e.g. relative
  ratio error, or map onto the [0,1] band scale) so a single severity vocabulary
  is coherent across metrics. `areas/reference_silhouette.py:200` already keys an
  action hint on `abs(aspect_ratio.delta) >= 0.18`; keep that hint working after
  rescaling.
- The dead band metrics: `mid_band_width_delta` (`0.35`-`0.65`) and
  `lower_band_width_delta` (`0.75`-`1.0`) are computed at
  `vision/silhouette.py:276-277` but `build_action_hints_from_silhouette`
  (`areas/reference_silhouette.py:82`) only consumes `upper_band_width_delta`,
  `left_projection_delta`, `right_projection_delta`, `aspect_ratio_delta`,
  `mask_iou`, and `contour_drift`. Either add bounded mid/lower-band action hints
  (mirroring the existing upper-band hint pattern at
  `areas/reference_silhouette.py:114`) or remove the unused metrics so the output
  carries no dead weight.
- Deterministic consistency score: add a render-vs-reference agreement signal
  computed each compare cycle. The lightweight default-on variant can be built
  from the already-available silhouette/contour quantities (e.g. a bounded
  composite of calibrated IoU + contour drift + band agreement) and stored as one
  advisory metric. The heavy variant (shared CLIP/DINO embedding distance, or a
  MEt3R/DUSt3R-style multi-view consistency network) must reuse the default-off
  sidecar config shape from `TASK-172` (`VisionSegmentationSidecarConfig` at
  `vision/config.py:390`, `VisionLocalizationConfig` at `:405`) — same `enabled:
  bool = False`, provider/endpoint/timeout fields — and stay packet-bounded.
- Convergence/stop signal: track the consistency score across cycles via the
  evaluation harness (`evaluation.py`). The score should move monotonically
  toward agreement as the reconstruction converges; a flat or worsening score
  across cycles is the signal to down-weight unverified VLM claims and to inform
  the orchestrator's stop decision. Surface it through the same compare-support
  evidence channel as silhouette metrics (`build_compare_support_evidence` at
  `areas/reference_silhouette.py:269`), keeping it advisory.
- Calibration regression: use `VisionGoldenScenario` / `evaluate_vision_result`
  (`vision/evaluation.py:142`/`:305`) and the existing
  `tests/fixtures/vision_eval/` golden bundles (e.g. `squirrel_head_to_body`,
  `synthetic_reference_mismatch`, `synthetic_no_change`,
  `synthetic_round_cutout`) so calibrated thresholds and the consistency score are
  pinned to repo-owned fixtures, not hand-picked constants.

### Research basis

- **MEt3R** (arXiv:2501.06336) — multi-view consistency score; the model for the
  optional heavy render-vs-reference variant.
- **Point-Bind** (arXiv:2309.00615) — shared embedding; the basis for a
  CLIP/DINO-style embedding-distance consistency check kept default-off.
- **IR3D-Bench** (arXiv:2506.23329) — deterministic-first evaluation; supports
  keeping the deterministic geometry check as the cross-check that down-weights
  advisory VLM claims rather than the other way around.

## Pseudocode

```python
def consistency_score(silhouette: SilhouetteAnalysis,
                      embedding: EmbeddingDistance | None) -> AdvisoryConsistency:
    # lightweight, always-on: derived from calibrated deterministic metrics
    iou = silhouette.metric("mask_iou").observed_value
    drift = silhouette.metric("contour_drift").observed_value
    band = mean(abs(silhouette.metric(m).delta) for m in BAND_METRICS)
    geometric = clamp01(0.5 * normalize_iou(iou) + 0.3 * (1 - drift) + 0.2 * (1 - band))

    # heavy variant only when the TASK-172 optional sidecar is explicitly enabled
    if embedding is not None:            # default-off, packet-bounded
        geometric = blend(geometric, embedding.agreement)

    return AdvisoryConsistency(
        score=geometric,
        not_truth_source=True,
        requires_deterministic_checks_for_correctness=True,
    )


def cross_check(vlm_findings, consistency, history):
    # down-weight unverified visual claims when geometry disagrees
    weighted = [f.with_weight(f.weight * consistency.score) for f in vlm_findings]
    converging = consistency.score >= history.last_score   # monotonic stop signal
    return weighted, converging


def calibrate_thresholds(golden_fixtures):
    # derive high/medium bands from labeled match/mismatch golden pairs
    matched = [iou_for(p) for p in golden_fixtures if p.relation == "match"]
    mismatched = [iou_for(p) for p in golden_fixtures if p.relation == "mismatch"]
    return derive_bands(matched, mismatched)           # replaces magic numbers
```

## Runtime / Security Contract Notes

- the consistency score and silhouette metrics stay advisory: `not_truth_source`
  / `requires_deterministic_checks_for_correctness`; they cannot pass gates or
  unlock tools
- deterministic inspection/assertion/silhouette own scene truth; the cross-check
  down-weights advisory VLM claims, it does not promote them
- magnitudes are proportional ratios versus the trusted reference anchor, never
  authoritative absolute measurements; the consistency score is a bounded [0,1]
  agreement signal, not a metric measurement
- the heavy embedding/MEt3R variant must stay default-off, advisory-only, and
  packet-bounded behind the existing `TASK-172` seam; no new always-on heavy
  dependency, and do not reopen the `TASK-140-06` provider-capability substrate
- do not emit raw coordinate tokens as primary evidence; the score and metrics
  are symbolic/scalar advisory evidence
- calibration must stay deterministic and reproducible from repo-owned fixtures;
  if fixtures are unavailable the analysis degrades to the existing
  `status="unavailable"` path rather than guessing

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_silhouette.py` — calibrated thresholds
  regression; `aspect_ratio_delta` rescaling; mid/lower-band metrics consumed or
  removed; deterministic consistency score bounds and monotonic behavior
- `tests/unit/adapters/mcp/test_vision_evaluation.py` — consistency score tracked
  across cycles as a convergence/stop signal on golden scenarios
- `tests/e2e/vision/test_reference_stage_silhouette_contract.py` — calibrated
  metrics and the advisory consistency score project through the compare-support
  evidence channel without changing gate authority
- `tests/fixtures/vision_eval/` — add/extend golden fixtures used for threshold
  calibration and consistency-score regression (re-measure before promotion)

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_VISION/HYBRID_LOOP_REAL_CREATURE_EVAL.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- board tracking remains on umbrella `TASK-183`
- no separate promoted board-row change is expected for this subtask unless it
  later becomes a standalone follow-on

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_silhouette.py tests/unit/adapters/mcp/test_vision_evaluation.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_stage_silhouette_contract.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py` (when Blender-backed capture/compare behavior is exercised)

## Validation Category

- deterministic cross-check and silhouette-calibration proof
