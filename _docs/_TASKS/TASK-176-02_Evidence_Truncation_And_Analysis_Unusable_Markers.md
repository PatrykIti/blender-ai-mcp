# TASK-176-02: Evidence-Truncation And Analysis-Unusable Markers

**Parent:** [TASK-176](./TASK-176_Capture_Failure_And_Evidence_Truncation_Signal_Surfacing.md)
**Status:** ✅ Done
**Completed:** 2026-05-30
**Priority:** 🔴 High
**Follow-on After:** [TASK-176-01](./TASK-176-01_Capture_Ok_And_Warning_Signals_For_Capture_Bundles.md)
**Objective:** Emit `evidence_truncated` + `omitted_count` wherever finding lists are hard-sliced, and add a top-level `analysis_unusable` flag (distinct from `confidence == 0.0`) so the orchestrator can tell "empty because the comparison was clean" from "empty because the analysis failed".
**Repository Touchpoints:** `server/adapters/mcp/vision/parsing.py`, `server/adapters/mcp/sampling/result_types.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `tests/unit/adapters/mcp/test_vision_parsing.py`, `tests/unit/adapters/mcp/test_vision_result_types.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/e2e/vision/test_external_contract_profile_compare_path.py`
**Acceptance Criteria:**
- every finding list that is hard-sliced emits `evidence_truncated=True` and an `omitted_count` equal to the number of deduped findings dropped, and emits `evidence_truncated=False` with `omitted_count=0` when nothing was dropped
- the truncation markers cover both the per-response slicing in `_normalize_payload` (`_bounded_string_list`, default `max_items=3`) and the cross-packet synthesis slicing in `synthesize_packet_vision_result` (`[:8]` / `[:6]`)
- `VisionAssistContract` gains additive, optional `evidence_truncated`, `omitted_count`, and `analysis_unusable` fields with reliability-neutral defaults so existing payloads stay valid
- repair payloads (`_repair_echo_payload`, `_repair_label_map_payload`, `_repair_unrecognized_payload`) carry `analysis_unusable=True`; a genuinely clean comparison carries `analysis_unusable=False` even when `confidence` is `0.0` or `None`
- `confidence` semantics are unchanged; `analysis_unusable` is an independent flag, and the two are never collapsed into one signal
- no new field marks a gate complete, unlocks a tool, or asserts scene truth

## Implementation Notes

- The per-response slicing site is `_normalize_payload`
  (`server/adapters/mcp/vision/parsing.py:1315`). It builds `visible_changes`,
  `shape_mismatches`, `proportion_mismatches`, `correction_focus`, and
  `next_corrections` through `_bounded_string_list`
  (parsing.py:318/322, default `max_items=3`) at lines 1326-1363. The slice
  silently drops items beyond `max_items` after dedupe, so the dropped count is
  computable as `len(deduped) - len(deduped[:max_items])`.
- `_bounded_string_list` currently returns only the truncated list. The cleanest
  additive approach is a sibling helper that returns both the bounded list and
  the omitted count (for example `_bounded_string_list_with_count(...)`), leaving
  the existing helper untouched for the many non-vision callers (the support /
  contact / planner paths at parsing.py:808-996 also use `_bounded_string_list`
  and should not be forced to surface truncation). `_normalize_payload` then
  aggregates the per-field omitted counts into the response-level
  `evidence_truncated` / `omitted_count`.
- The cross-packet slicing site is `synthesize_packet_vision_result`
  (`server/adapters/mcp/areas/reference_compare_packets.py:1258`). It slices
  `visible_changes` to `[:8]` (line 1273), `shape_mismatches` /
  `proportion_mismatches` / `correction_focus` / `next_corrections` to `[:6]`
  (lines 1276-1285), and `likely_issues` / `recommended_checks` to `[:6]` at
  lines 1358 and 1360. This file already carries an additive omission precedent:
  `budget_notes` (reference_compare_packets.py:967-989) records when packet
  policy dropped captures or split references. The new `evidence_truncated` /
  `omitted_count` should follow that same additive-note posture but on the
  result contract, computing the omitted count before the slice and summing it
  across the merged fields.
- The empty-but-valid repair gap is in the three repair builders at
  parsing.py:205-272. Each returns empty `visible_changes` /
  `shape_mismatches` / `proportion_mismatches` lists with `confidence: 0.0`.
  Downstream `confidence == 0.0` is indistinguishable from "model unsure but
  scene fine", which is why a failed parse can read like a clean comparison. Set
  `analysis_unusable: True` in each repair payload and default `analysis_unusable:
  False` everywhere else, including `synthesize_packet_vision_result` and the
  clean-packet path, so the orchestrator gets an explicit "do not read this as a
  clean result" signal that does not depend on the confidence value.
- Keep the boundary intact: `synthesize_packet_vision_result` already constructs
  `VisionBoundaryPolicyContract()` (reference_compare_packets.py:1369) and the
  contract default in `result_types.py:170` keeps `not_truth_source` /
  `requires_deterministic_checks_for_correctness`. The new fields are reliability
  metadata layered on top, never a replacement for deterministic truth.
- The entry point that returns the parsed contract is `parse_vision_output_text`
  (parsing.py:2131); the repair dispatch at parsing.py:2235-2246 selects which
  `_repair_*` builder runs, so the `analysis_unusable=True` marker is set inside
  those builders and flows through unchanged.
- Research basis (cite by name + arXiv id): LL3M (arXiv:2508.08228) motivates the
  Critic/Verify pattern where an empty or failed analysis must be marked unusable
  rather than presented as a clean pass; DiffuRank (arXiv:2404.07984) and
  3DSRBench (arXiv:2412.07825) explain why silently dropping evidence (truncated
  mismatch lists) is dangerous for downstream spatial reasoning, since the
  orchestrator over-trusts an incomplete picture exactly when the captures were
  ambiguous.

## Pseudocode

```python
# parsing.py
def _bounded_string_list_with_count(
    items: list[str], *, max_items: int = 3, prune_unhelpful: bool = False
) -> tuple[list[str], int]:
    deduped = _dedupe_string_list(items)
    if prune_unhelpful:
        deduped = _prune_unhelpful_correction_items(deduped)
    bounded = deduped[:max_items]
    return bounded, max(0, len(deduped) - len(bounded))


# inside _normalize_payload:
omitted_total = 0
visible_changes, dropped = _bounded_string_list_with_count(visible_changes)
omitted_total += dropped
shape_mismatches, dropped = _bounded_string_list_with_count(
    _coerce_string_list(_first_nonempty_value(parsed, _SHAPE_MISMATCHES_ALIASES)),
    prune_unhelpful=True,
)
omitted_total += dropped
# ... same for proportion_mismatches / correction_focus / next_corrections ...
evidence_truncated = omitted_total > 0
# analysis_unusable defaults False on the normal parse path
# repair builders set analysis_unusable=True explicitly


# reference_compare_packets.py: synthesize_packet_vision_result
def _slice_with_count(items: list[str], limit: int) -> tuple[list[str], int]:
    return items[:limit], max(0, len(items) - limit)


visible_changes, dropped_vc = _slice_with_count(_unique_preserving_order([...]), 8)
shape_mismatches, dropped_sm = _slice_with_count(_unique_preserving_order([...]), 6)
# ... etc for proportion_mismatches / correction_focus / next_corrections ...
synth_omitted = dropped_vc + dropped_sm + ...
return VisionAssistContract(
    ...,
    evidence_truncated=synth_omitted > 0,
    omitted_count=synth_omitted,
    analysis_unusable=False,
    boundary_policy=VisionBoundaryPolicyContract(),
)
```

## Runtime / Security Contract Notes

- Vision stays advisory. `evidence_truncated`, `omitted_count`, and
  `analysis_unusable` are reliability metadata only; they are `not_truth_source`
  and `requires_deterministic_checks_for_correctness`, and must not mark a gate
  complete or unlock a tool.
- `analysis_unusable` is deliberately independent of `confidence`. The two must
  never be merged; an unusable analysis can occur at any confidence value, and a
  low-confidence-but-clean comparison must stay usable.
- No magnitudes and no raw coordinate tokens are introduced; the markers are a
  boolean plus an integer count plus an existing boundary contract.
- The change is additive: existing serialized `VisionAssistContract` payloads and
  fixtures remain valid because every new field has a reliability-neutral default
  (`evidence_truncated=False`, `omitted_count=0`, `analysis_unusable=False`).

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_parsing.py` (assert `_normalize_payload`
  sets `evidence_truncated=True` and the correct `omitted_count` when more than
  `max_items` findings are present, and `False` / `0` otherwise; assert each
  `_repair_*` payload sets `analysis_unusable=True` while keeping `confidence ==
  0.0`)
- `tests/unit/adapters/mcp/test_vision_result_types.py` (assert the new fields
  exist with reliability-neutral defaults and that the boundary policy still
  asserts `not_truth_source`)
- `tests/unit/adapters/mcp/test_reference_compare_packets.py` (assert
  `synthesize_packet_vision_result` reports truncation when merged findings
  exceed the `[:8]` / `[:6]` caps and `analysis_unusable=False` on a clean
  synthesis)
- `tests/e2e/vision/test_external_contract_profile_compare_path.py` (prove an
  unusable/echoed external response surfaces `analysis_unusable=True` distinct
  from a clean low-confidence pass end to end)

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- board tracking remains on umbrella `TASK-176`
- no separate promoted board-row change is expected for this subtask unless it
  later becomes a standalone follow-on

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_parsing.py tests/unit/adapters/mcp/test_vision_result_types.py tests/unit/adapters/mcp/test_reference_compare_packets.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`

## Validation Category

- evidence-reliability marker proof
