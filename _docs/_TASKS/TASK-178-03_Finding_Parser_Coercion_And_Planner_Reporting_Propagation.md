# TASK-178-03: Finding Parser Coercion And Planner/Reporting Propagation

**Parent:** [TASK-178](./TASK-178_Structured_Per_Finding_Compare_Schema.md)
**Status:** ✅ Done
**Completed:** 2026-05-30
**Priority:** 🔴 High
**Follow-on After:** [TASK-178-01](./TASK-178-01_Structured_Vision_Finding_Contract_Model.md), [TASK-178-02](./TASK-178-02_Structured_Finding_Prompt_And_Response_Schema_Emission.md)
**Objective:** Coerce and clamp parsed structured findings in `vision/parsing.py` (validate compare and per-finding `confidence` to `[0, 1]`, normalize `axis` / `direction` to the fixed vocabularies, drop out-of-vocabulary `target_label` to `None`, default missing fields safely, and keep the flat string projection populated), then propagate object + axis + `magnitude_ratio` into macro reporting (`vision/reporting.py`) and the repair planner (`areas/reference_planner.py`).

**Repository Touchpoints:** `server/adapters/mcp/vision/parsing.py`, `server/adapters/mcp/vision/reporting.py`, `server/adapters/mcp/areas/reference_planner.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`

**Acceptance Criteria:**
- `_normalize_payload` (`vision/parsing.py:1315`) parses structured finding arrays into `VisionFinding` items and also derives the legacy flat string lists from them for backward compatibility
- compare `confidence` (`vision/parsing.py:1365-1367`) is clamped to `[0, 1]` instead of only type-checked; values outside the range are clamped, not passed through or silently nulled
- each per-finding `confidence` is clamped to `[0, 1]`; out-of-vocabulary `axis` / `direction` normalize to `none`; out-of-vocabulary or empty `target_label` becomes `None`; a non-numeric `magnitude_ratio` becomes `None`
- when a model returns only flat strings (weak model or `google_family_compare`), parsing still yields the same `VisionAssistContract` with empty structured finding lists and populated legacy string lists (no regression)
- structured findings still respect the existing bounded-list caps (the 3-item cap at `vision/parsing.py:318`) so output stays packet-bounded
- `vision/reporting.py:_vision_recommendations_for_macro` (`:30`) can include `target_label` + `axis` + `magnitude_ratio` in the recommendation reason instead of a generic "vision flagged mismatches" string
- `areas/reference_planner.py` can route on structured `target_label` / `axis` / `magnitude_ratio` (`_local_form_reason` at `:408`, `_proportion_planner_blockers` at `:368`) rather than re-deriving them from free strings

## Implementation Notes

- the compare parse entry point is `_normalize_payload(parsed, request)`
  (`server/adapters/mcp/vision/parsing.py:1315`). It currently coerces every
  geometric field with `_coerce_string_list(...)` and bounds them via
  `_bounded_string_list(...)` (cap `max_items=3` at `:318`):
  - `shape_mismatches` (`:1327`), `proportion_mismatches` (`:1331`),
    `correction_focus` (`:1335`), `next_corrections` (`:1355`)
  - the final dict is assembled at `:1415-1428`
- add structured-finding coercion alongside the existing string coercion:
  - read `parsed.get("shape_findings")` / `parsed.get("proportion_findings")`
    (and any aliases) into a list of dicts
  - per item: keep `finding` as a stripped string, normalize `axis` /
    `direction` against the TASK-178-01 `Literal` vocabularies (unknown ->
    `none`), drop `target_label` to `None` if it is not in the canonical role
    set, coerce `magnitude_ratio` to `float` or `None`, clamp per-finding
    `confidence` to `[0, 1]`
  - apply the same `_bounded_string_list`-equivalent cap (3 items) to keep the
    output packet-bounded
  - derive the legacy `shape_mismatches` / `proportion_mismatches` lists from the
    structured findings (via the TASK-178-01 projection helper) when the model
    returned structured findings, otherwise fall back to the existing string
    path unchanged
- fix the compare-confidence clamp. Today `:1365-1367` does:

  ```python
  confidence = parsed.get("confidence")
  if not isinstance(confidence, (int, float)) and confidence is not None:
      confidence = None
  ```

  This validates type but not range, so `7` or `-0.3` flow through. Clamp it.
- `vision/reporting.py:_vision_recommendations_for_macro` (`:30`) builds
  `MacroVerificationRecommendationContract` items from `result.shape_mismatches`
  / `result.proportion_mismatches` (`:50-66`) with generic reasons. When
  structured findings are present, enrich the `reason` with `target_label`,
  `axis`, and `magnitude_ratio` so the macro follow-up is object/axis-aware. Keep
  the existing generic reasons as the fallback when only flat strings exist.
- `areas/reference_planner.py` consumes vision evidence through
  `ReferenceCorrectionVisionEvidenceContract`
  (`_local_form_reason` at `:408` reads `correction_focus` / `shape_mismatches`
  / `next_corrections`; `_proportion_planner_blockers` at `:368`). With the
  additive `findings: list[VisionFinding]` channel from TASK-178-01, the planner
  can prefer the structured `target_label` + `axis` + `magnitude_ratio` when
  present and fall back to the string lists otherwise. Deterministic truth and
  silhouette metrics remain the gate authority; structured findings only inform
  focus/ranking.
- techniques to cite:
  - **SpatialVLM** (arXiv:2401.12168) / **SD-VLM** (arXiv:2509.17664) — the
    proportional-ratio framing justifies clamping/normalizing `magnitude_ratio`
    as a ratio rather than trusting it as an absolute value
  - **SpatialRGPT** (arXiv:2406.01584) — the structured `axis` / `direction`
    decomposition is what the planner now routes on instead of free text
  - **SceneVerse** (arXiv:2401.09340) — symbolic `target_label` binding is what
    lets the planner avoid re-deriving the target by string matching

## Pseudocode

```python
def _clamp_unit(value: object) -> float | None:
    if not isinstance(value, (int, float)):
        return None
    return max(0.0, min(1.0, float(value)))


_AXIS_VOCAB = {"x", "y", "z", "width", "height", "depth", "none"}
_DIRECTION_VOCAB = {
    "too_large", "too_small", "too_wide", "too_narrow",
    "too_tall", "too_short", "shifted", "rotated", "none",
}


def _coerce_findings(raw: object, *, canonical_roles: set[str]) -> list[dict]:
    findings: list[dict] = []
    for item in raw if isinstance(raw, list) else []:
        if not isinstance(item, dict):
            continue
        text = str(item.get("finding") or "").strip()
        if not text:
            continue
        axis = str(item.get("axis") or "none").strip().lower()
        direction = str(item.get("direction") or "none").strip().lower()
        label = str(item.get("target_label") or "").strip()
        ratio = item.get("magnitude_ratio")
        findings.append({
            "finding": text,
            "view_id": (str(item.get("view_id")).strip() or None) if item.get("view_id") else None,
            "target_label": label if label in canonical_roles else None,
            "axis": axis if axis in _AXIS_VOCAB else "none",
            "direction": direction if direction in _DIRECTION_VOCAB else "none",
            "magnitude_ratio": float(ratio) if isinstance(ratio, (int, float)) else None,
            "reference_id": (str(item.get("reference_id")).strip() or None) if item.get("reference_id") else None,
            "confidence": _clamp_unit(item.get("confidence")),
        })
    return findings[:3]  # keep the existing packet-bounded cap


# Compare-level confidence clamp (replaces parsing.py:1365-1367):
confidence = _clamp_unit(parsed.get("confidence"))
```

## Runtime / Security Contract Notes

- parsed structured findings stay advisory: the resulting `VisionAssistContract`
  keeps `boundary_policy.not_truth_source` and
  `requires_deterministic_checks_for_correctness`. The planner uses findings only
  to bias focus and ranking; deterministic truth / silhouette metrics remain the
  gate and completion authority.
- `magnitude_ratio` is clamped/normalized as a proportional ratio only; it is
  never promoted to an absolute measurement and never used to pass a gate.
- normalization is fail-closed: unknown `axis` / `direction` -> `none`,
  out-of-vocabulary `target_label` -> `None`, non-numeric ratio/confidence ->
  `None`/clamped, so a malformed model response cannot smuggle authority or
  out-of-range signals downstream.
- planner and reporting changes operate on already-captured compare results, so
  they do not touch Blender main-thread state directly. If a planner-driven macro
  later mutates the scene, that path already goes through the existing
  `capture_scene_state` / `restore_scene_state` reversibility seams and is out of
  scope for this parsing/propagation subtask.

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_reference_compare_packets.py`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- add/update a `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- board tracking remains on umbrella `TASK-178`
- no separate promoted board-row change is expected for this subtask unless it
  later becomes a standalone follow-on

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_reference_compare_packets.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py` (when planner-driven Blender behavior changes)

## Validation Category

- parser-coercion / planner-propagation proof
