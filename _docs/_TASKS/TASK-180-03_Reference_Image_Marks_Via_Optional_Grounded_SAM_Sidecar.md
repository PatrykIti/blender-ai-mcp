# TASK-180-03: Reference-Image Marks Via Optional Grounded-SAM Sidecar

**Parent:** [TASK-180](./TASK-180_Set_Of_Mark_Object_Bound_Visual_Marks.md)
**Status:** ✅ Done
**Priority:** 🟠 Medium
**Follow-on After:** [TASK-180-02](./TASK-180-02_Stable_Mark_Identifiers_Across_Views_And_Iterations.md), [TASK-172-03-01](./TASK-172-03-01_Localization_Runtime_Config_And_Provider_Boundary.md)
**Objective:** When the optional, default-off Grounded-SAM sidecar is enabled, mark the corresponding parts on the REFERENCE image with the same stable ID scheme used on the render, so render-vs-reference correspondence is explicit. When the sidecar is disabled (the default), degrade gracefully to render-only marks with no behavior regression.

**Repository Touchpoints:** `server/adapters/mcp/vision/reference_support.py`, `server/adapters/mcp/vision/config.py`, `server/adapters/mcp/vision/runtime.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `tests/unit/adapters/mcp/test_vision_runtime_config.py`, `tests/e2e/vision/test_reference_stage_silhouette_contract.py`

**Acceptance Criteria:**
- with the localization/Grounded-SAM sidecar off (default), the compare path emits render-only marks and there is no regression versus the current no-overlay behavior; no sidecar call is attempted.
- with the sidecar enabled, the reference image receives marks for the parts it can ground, using the SAME mark IDs as the render via the per-packet `mark_id_map` so `mark 3` means the same part on both images.
- reference-side marks are advisory and packet-bounded: the number of grounded queries is capped by the existing `max_candidates` budget, and a sidecar timeout or failure degrades to render-only marks instead of failing the compare.
- a typed per-mark provenance flag distinguishes render-side marks (deterministic) from reference-side marks (grounded by the optional sidecar), so downstream parsing and operators can tell which marks are model-grounded.

## Implementation Notes

- Grounded SAM (arXiv:2401.14159) is the technique: open-vocabulary detection
  (GroundingDINO) plus SAM segmentation to localize and mask named parts on an
  arbitrary image; here it grounds the registered part labels on the REFERENCE so
  the same numbered marks can be drawn there. SAM2 (arXiv:2408.00714) is the
  stable-identity reference for keeping a grounded part's identity consistent;
  the ID itself comes from TASK-180-02's registry map, not from the detector.
- This is an OPTIONAL, default-off path on the existing TASK-172 seam. Reuse it
  exactly; do not add a new provider substrate:
  - `runtime.py:230-252` already builds `VisionLocalizationConfig` /
    `VisionSegmentationSidecarConfig` only when `VISION_LOCALIZATION_ENABLED` /
    `VISION_SEGMENTATION_ENABLED` are set; reference marking rides this gate.
  - `VisionLocalizationConfig` (`config.py:405`) carries `enabled=False`,
    `provider_name`, `endpoint`, `timeout_seconds`, `max_candidates` (1..32);
    `VisionLocalizationCandidate` (`config.py:420`) already carries
    `box_xyxy`, `target_view`, `confidence`, `crop_path`, keyed by `packet_id`
    and `query_label`.
  - `reference_compare_packets.py` already builds the localization request
    payload (`_build_compare_localization_request_payload` ~:339, with
    `query_labels` from `_query_labels_for_packet`) and posts it
    (`_post_sidecar_payload` ~:361). Extend the SAME flow to map returned
    candidates back to mark IDs via the packet `mark_id_map`.
  - `reference_support.py` is the optional advisory-only RU support adapter
    module; keep the reference-marking adapter in the same advisory style
    (`_redact_local_paths`, bounded payloads, provider-neutral merge).
- Graceful degradation is the contract, not a nicety. If the sidecar is off, or
  returns nothing, or times out, the result is render-only marks. The compare
  path must never block on reference marking, and a partial reference grounding
  (some parts found, some not) must mark only the found parts and leave the rest
  render-only.
- Provenance: extend the overlay mark contract so each reference-side mark
  records `source="grounded_sam_sidecar"` versus the render-side
  `source="deterministic_projection"`, so TASK-180-04 and operator docs can
  surface which marks were model-grounded. Do not collapse the two.
- Do not emit reference box coordinates as primary evidence; the boxes stay
  internal to drawing the mark, and only the symbolic mark ID + provenance flag
  flow into the correspondence layer.

## Pseudocode

```python
async def mark_reference_with_grounded_sam(packet, mark_id_map, localization_config):
    if not localization_config or not localization_config.enabled:
        return []  # render-only marks; default path, no regression
    query_labels = query_labels_for_packet(packet)  # bounded
    try:
        candidates = await post_localization_sidecar(
            packet, query_labels, max_candidates=localization_config.max_candidates,
            timeout=localization_config.timeout_seconds,
        )
    except (SidecarTimeout, SidecarError):
        return []  # degrade to render-only, do not fail compare
    reference_marks = []
    for cand in candidates:
        object_name = match_query_to_object(cand.query_label, mark_id_map)
        if object_name is None:
            continue  # ungrounded; leave render-only
        reference_marks.append(VisionOverlayMarkContract(
            mark_id=mark_id_map[object_name],
            object_name=object_name,
            status="placed",
            source="grounded_sam_sidecar",
            image_side="reference",
        ))
    return reference_marks
```

## Runtime / Security Contract Notes

- the Grounded-SAM reference-marking sidecar stays DEFAULT-OFF, advisory-only,
  and packet-bounded, reusing the TASK-172 optional-runtime seam; it must not be
  promoted to default-on and must not reopen the TASK-140-06 provider substrate.
- reference marks are model-grounded interpretation, not truth: a reference mark
  never asserts correctness, never marks a gate complete, and never unlocks a
  tool. `boundary_policy` stays `not_truth_source=True`,
  `requires_deterministic_checks_for_correctness=True`.
- fail-closed and bounded: sidecar timeout/error/empty -> render-only marks;
  query count capped by `max_candidates`; local paths redacted on any
  outbound/inbound payload (`_redact_local_paths`).
- no raw reference boxes leave as primary evidence; only the symbolic mark ID and
  the `source` provenance flag propagate.

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py` (sidecar off by default; enabling builds the config; provenance flag wiring)
- new `tests/unit/adapters/mcp/test_reference_mark_grounding.py` (candidate-to-mark-id mapping; timeout/empty -> render-only; partial grounding leaves unfound parts render-only)
- `tests/e2e/vision/test_reference_stage_silhouette_contract.py` (degrade-to-render-only path produces no regression when the sidecar is disabled)

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md` (optional Grounded-SAM env keys)

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- board tracking remains on umbrella `TASK-180`
- no separate promoted board-row change is expected for this subtask
- 2026-05-31: completed. The existing default-off localization sidecar now
  projects bounded candidates back to packet `mark_id_map` entries and records
  reference-side `VisionOverlayMarkContract` rows with
  `source="grounded_sam_sidecar"` / `image_side="reference"`. Disabled, empty,
  timeout, or failed sidecar paths still degrade to render-only marks.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`  # when reference-overlay Blender behavior changes
- 2026-05-31 focused validation:
  `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_vision_prompting.py -q` as part of the targeted MCP lane -> 180 passed

## Validation Category

- optional advisory sidecar activation and graceful-degradation proof
