# TASK-179-02: Per-Object Mask IoU In Silhouette Evidence

**Parent:** [TASK-179](./TASK-179_Blender_Depth_Normal_And_Object_ID_Auxiliary_Passes.md)
**Status:** ✅ Done
**Completed:** 2026-05-30
**Priority:** 🔴 High
**Follow-on After:** [TASK-179-01](./TASK-179-01_Addon_Object_ID_Depth_And_Normal_Render_Passes.md)
**Objective:** Extend `silhouette.py` to compute deterministic per-object mask IoU from the object-ID pass produced by TASK-179-01, in addition to the existing whole-frame silhouette IoU, so geometric mismatch can be attributed to a specific registered part instead of only the whole form. The per-object metrics are projected into the staged compare payload through `reference_silhouette.py` and reuse the existing segmentation-shaped contracts, while remaining deterministic and advisory.
**Repository Touchpoints:** `server/adapters/mcp/vision/silhouette.py`, `server/adapters/mcp/areas/reference_silhouette.py`, `server/adapters/mcp/contracts/reference.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/fixtures/vision_eval/`
**Acceptance Criteria:**
- `silhouette.py` exposes a deterministic per-object IoU helper that, given the object-ID index map (`{pass_index: object_name}`) and the rendered object-ID image, derives one binary mask per registered object and computes IoU against the corresponding reference region
- per-object IoU is **additive**: the existing whole-frame `mask_iou`, `contour_drift`, `aspect_ratio_delta`, and band metrics in `build_silhouette_analysis(...)` are unchanged
- when the object-ID pass is unavailable or a part is not present in the view, the per-object result is a typed `status: "unavailable"` for that part with a note, never a fabricated score
- `reference_silhouette.py` projects per-object metrics into the compare payload so a mismatch can name the specific part that diverged
- per-object thresholds are documented and calibrated against `tests/fixtures/vision_eval` golden fixtures rather than copying the existing uncalibrated whole-frame magic numbers blindly

## Implementation Notes

- The current evidence path is whole-frame only:
  `server/adapters/mcp/vision/silhouette.py:233-256` computes a single
  `intersection / union` over one normalized largest-component mask, with
  uncalibrated thresholds (`mask_iou` `high=0.35`, `medium=0.18`). `_extract_mask_from_image`
  (`:108-155`) only ever isolates one foreground blob (alpha or Otsu), so it
  cannot separate parts that touch or overlap.
- The object-ID pass from TASK-179-01 makes per-part masks deterministic: each
  registered object has a unique `pass_index`, so the per-object mask is exactly
  `object_id_array == pass_index`. This needs **no SAM** and no connected-component
  guessing; reuse the existing `_crop_bbox` (`:158-166`) and `_normalize_mask`
  (`:169-177`) helpers to bbox-normalize each per-object mask before IoU, matching
  the existing `alignment_mode: "bbox_normalized"`.
- For the reference side, when a deterministic reference object-ID pass is not
  available (real reference photos have no Blender pass), per-object IoU is only
  computed for the *capture* against the whole-frame reference region, and the
  result is clearly marked as capture-side-only attribution. The optional
  monocular-depth/reference hook is out of scope here (it lives in the umbrella's
  optional seam, not this slice).
- Contract reuse: the repo already has
  `ReferencePartSegmentationContract` / `ReferencePartSegmentationPartContract`
  (`server/adapters/mcp/contracts/reference.py:769-786`) shaped for part-aware
  evidence (`part_label`, `mask_path`, `confidence`, advisory_only=True). Populate
  a deterministic variant of these (or add per-object metric fields to
  `ReferenceSilhouetteAnalysisContract` at `reference.py:748-758`) so the
  per-object IoU is typed and projected through
  `reference_silhouette.py:build_silhouette_analysis_payload(...)`. Keep
  `advisory_only=True` and avoid emitting raw box coordinates as the primary
  signal — surface the part label + IoU ratio + symbolic severity instead.
- Severity calibration: do **not** copy the whole-frame `high=0.35` threshold
  blindly. Pick per-object thresholds and validate them against the golden
  reference/capture pairs in `tests/fixtures/vision_eval/`, recording the chosen
  values in the test and docs (the research caveat: cited gains are not
  Blender-vs-reference, so thresholds must be re-measured here).
- Research basis (cite, do not implement VLM chain-of-thought): per-part
  geometric attribution is the deterministic analogue of the part-aware spatial
  channels discussed in the spatial-reasoning survey (arXiv:2405.10255) and the
  depth-aware encoders SpatialRGPT (arXiv:2406.01584) / SD-VLM
  (arXiv:2509.17664); per-part IoU + ratios are preferred over coordinate tokens
  because relations/ratios outperform raw coords for spatial reasoning.

## Pseudocode

```python
def build_per_object_iou(object_id_image, index_map, reference_region_mask):
    object_id = load_index_array(object_id_image)   # H x W ints
    per_object = []
    for pass_index, object_name in index_map.items():
        capture_mask = object_id == pass_index
        if not capture_mask.any():
            per_object.append({"object_name": object_name, "status": "unavailable",
                               "reason": "not_present_in_view"})
            continue
        cap_crop, _ = _crop_bbox(capture_mask)
        cap_norm = _normalize_mask(cap_crop)
        ref_norm = _normalize_mask(reference_region_mask)   # whole-frame ref when no ref id-pass
        inter = float(np.logical_and(cap_norm, ref_norm).sum())
        union = float(np.logical_or(cap_norm, ref_norm).sum()) or 1.0
        iou = inter / union
        per_object.append({
            "object_name": object_name,
            "status": "available",
            "mask_iou": iou,
            "severity": _metric_severity(iou - 1.0, high=PER_OBJECT_HIGH, medium=PER_OBJECT_MED),
        })
    return per_object
```

## Runtime / Security Contract Notes

- Per-object IoU is deterministic and bounded, but it is **evidence, not gate
  authority**: it cannot mark a creature part gate complete or unlock a tool, and
  it keeps `not_truth_source` / `requires_deterministic_checks_for_correctness`
  framing when surfaced toward the orchestrator.
- IoU is a ratio in [0, 1]; do not present it as an absolute measurement of part
  size. Any size/scale magnitude must be a proportional ratio against a trusted
  reference anchor.
- Prefer symbolic part-name + severity + IoU ratio in the projected evidence;
  raw mask bbox coordinates stay available on demand only, never as the primary
  spatial signal.
- Fail closed: a missing object-ID pass or an absent part yields a typed
  `unavailable` per-object result, never a fabricated IoU.

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- a new focused unit lane for `silhouette.py` per-object IoU (deterministic masks,
  unavailable-part path, bbox normalization parity with whole-frame)
- `tests/fixtures/vision_eval/` golden fixtures for per-object threshold
  calibration

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- board tracking remains on umbrella `TASK-179`
- no separate promoted board-row change is expected for this subtask unless it
  later becomes a standalone follow-on

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Validation Category

- deterministic per-object geometric-evidence proof
