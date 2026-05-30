# TASK-180-04: Mark-Keyed Findings, Correspondence Table And Validity Retry

**Parent:** [TASK-180](./TASK-180_Set_Of_Mark_Object_Bound_Visual_Marks.md)
**Status:** ✅ Done
**Completed:** 2026-05-30
**Completion Note:** Server-side core shipped (changelog 381): mark_id on VisionFindingContract + parser coercion + build_mark_correspondence_table with VLM-Grounder validity guard. Live overlay wiring into the compare flow remains addon + E2E follow-on.
**Priority:** 🔴 High
**Follow-on After:** [TASK-180-02](./TASK-180-02_Stable_Mark_Identifiers_Across_Views_And_Iterations.md), [TASK-180-03](./TASK-180-03_Reference_Image_Marks_Via_Optional_Grounded_SAM_Sidecar.md)
**Objective:** Require the VLM to key its compare findings to mark IDs, parse those mark-keyed findings into an object-correspondence table mapped back to scene `object_name`s, and add a validity-retry guard that rejects findings citing marks that do not exist in the rendered mark set.

**Repository Touchpoints:** `server/adapters/mcp/vision/prompting.py`, `server/adapters/mcp/vision/parsing.py`, `server/adapters/mcp/sampling/result_types.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/fixtures/vision_eval/`

**Acceptance Criteria:**
- the compare payload text presents the IMAGES roster with the per-image mark context (which mark IDs appear on which view), replacing the current flat, caption-less roster (`image_lines = [f"- {image.role}: {image.label or image.role}"]` ~:497/539/629) for overlay-bearing packets.
- the compare JSON schema allows mark-keyed findings (each finding may carry a `mark_id`) instead of only bare `string[]` (`prompting.py` schema ~:1259-1300; the google_family compare branch ~:1245 must not silently drop the mark fields).
- the parser builds an object-correspondence table: `mark_id -> object_name (+ role)` resolved from the packet `mark_id_map`, with any attached magnitude expressed as a proportional ratio versus a named anchor, never an absolute measurement.
- a validity-retry guard rejects findings whose `mark_id` is not in the rendered mark set; the rejection is recorded in the result (a note / dropped-marks list), not silently swallowed, and on first invalid response the guard requests one bounded re-emission constrained to valid marks.
- the typed result (`VisionAssistContract`) carries the correspondence table and the validity outcome while keeping `boundary_policy.not_truth_source=True` and `requires_deterministic_checks_for_correctness=True`.

## Implementation Notes

- Set-of-Mark (arXiv:2310.11441) is the prompting contract: the model answers by
  referring to the overlaid numeric marks, so findings become addressable. The
  validity-retry guard follows VLM-Grounder (arXiv:2410.13860): when a model
  references a mark/region that does not exist, reject and re-query under a
  constraint rather than trusting a hallucinated reference. GPT4Scene
  (arXiv:2501.01428) is the cross-view correspondence basis for tabulating the
  same mark across views back to one object.
- Payload text (`prompting.py`): the current roster lines are flat and
  caption-less (`_build_gemini_compare_payload_text` ~:497,
  `_build_reference_understanding_payload_text` ~:539,
  `build_vision_payload_text` packet branch ~:629). For overlay-bearing packets,
  emit the mark legend (mark_id -> view(s) it appears on, and whether a matching
  reference mark exists from TASK-180-03) and instruct the model to key each
  shape/proportion finding to a `mark_id`. Keep the existing advisory rules
  (no passed/final-completion claims; deterministic checks decide correctness)
  and add: magnitudes must be proportional ratios versus a named anchor, never
  absolute; do not restate coordinates.
- Schema (`prompting.py` ~:1259-1300): extend `shape_mismatches` /
  `proportion_mismatches` (or add a parallel mark-keyed array) so each item may
  carry `mark_id: int | null`. The google_family compare branch (~:1245) must
  carry the same mark fields rather than dropping them, so both transmit paths
  (`backends.py:849-916`) produce mark-keyed evidence.
- Parser (`parsing.py`): build the correspondence table from the packet
  `mark_id_map` (TASK-180-02). Today the parser bounds finding lists to 3 items
  (`_bounded_string_list` `max_items=3` ~:318) and does not range-validate
  compare confidence (~:1365-1367). When tabulating mark-keyed findings, keep a
  bounded table but do not blindly truncate distinct valid marks below the
  registered part count, and validate that any cited `mark_id` exists. Resolve
  `role` from `assembled_target_scope.object_roles` when present.
- Validity-retry guard: collect cited `mark_id`s, diff against the rendered mark
  set; if any are invalid, drop them, record them in a `rejected_mark_ids` /
  notes field, and (once) re-request a bounded compare constrained to the valid
  mark set. The guard is fail-closed: an unresolvable mark is dropped, never
  promoted to an unverified object edit.
- Contract (`result_types.py`): add a typed `VisionMarkCorrespondenceContract`
  (mark_id, object_name, role, image_sides, proportional_ratio_vs_anchor) and a
  `object_correspondence: list[...]` plus `rejected_mark_ids: list[int]` on
  `VisionAssistContract`, next to the existing `shape_mismatches`,
  `proportion_mismatches`, and `boundary_policy` fields. Keep
  `truth_source="vision_assist"` and the boundary defaults.

## Pseudocode

```python
def parse_mark_keyed_findings(parsed, packet_mark_id_map, rendered_mark_ids):
    valid_ids = set(rendered_mark_ids)
    rejected: list[int] = []
    table: list[VisionMarkCorrespondenceContract] = []
    for item in parsed.get("shape_mismatches", []) + parsed.get("proportion_mismatches", []):
        mark_id = coerce_int_or_none(item.get("mark_id"))
        if mark_id is None:
            continue  # unkeyed prose retained separately, not tabulated
        if mark_id not in valid_ids:
            rejected.append(mark_id)  # surfaced, not silently dropped
            continue
        object_name = invert(packet_mark_id_map)[mark_id]
        table.append(VisionMarkCorrespondenceContract(
            mark_id=mark_id,
            object_name=object_name,
            role=role_for(object_name),
            proportional_ratio_vs_anchor=normalize_ratio(item.get("ratio")),  # never absolute
        ))
    return table, rejected

def vision_compare_with_validity_retry(request, mark_id_map, rendered_mark_ids):
    parsed = run_vision_compare(request)
    table, rejected = parse_mark_keyed_findings(parsed, mark_id_map, rendered_mark_ids)
    if rejected and not request.is_retry:
        parsed = run_vision_compare(constrain_to_marks(request, sorted(rendered_mark_ids)))
        table, rejected = parse_mark_keyed_findings(parsed, mark_id_map, rendered_mark_ids)
    return build_assist_contract(parsed, object_correspondence=table, rejected_mark_ids=rejected)
```

## Runtime / Security Contract Notes

- mark-keyed findings and the correspondence table are VLM interpretation; they
  stay advisory. The result keeps `boundary_policy.not_truth_source=True` and
  `requires_deterministic_checks_for_correctness=True`; the table never marks a
  gate complete and never unlocks a tool.
- magnitudes attached to marks are proportional ratios versus a named anchor
  only; reject or normalize any absolute measurement, because VLM metric
  estimates are unreliable (~37% within 2x).
- the validity-retry guard is fail-closed: invalid marks are dropped and
  surfaced; the model is re-queried at most once under a valid-mark constraint;
  no hallucinated mark ever becomes an actioned object reference.
- no VLM-side chain-of-thought for spatial judgments about the marks; the
  payload requests the correspondence answer directly, leaving spatial reasoning
  to the orchestrator (CoT regresses spatial benchmarks).
- coordinates stay off the primary evidence path; the correspondence table is
  symbolic (mark_id + object_name + role + ratio).

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_compare_packets.py` (mark-keyed findings parse into a correspondence table mapped to `object_name`; role resolution from `object_roles`)
- new `tests/unit/adapters/mcp/test_mark_validity_retry.py` (non-existent mark id is rejected and surfaced; one bounded retry constrained to valid marks; fail-closed when retry still invalid)
- `tests/unit/adapters/mcp/test_contract_payload_parity.py` (mark fields survive both generic and google_family compare schemas / transmit paths)
- `tests/fixtures/vision_eval/` (golden fixtures asserting correspondence-table accuracy and that ratios are proportional, not absolute; re-measure before any promotion per the umbrella research caveat)

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- board tracking remains on umbrella `TASK-180`
- no separate promoted board-row change is expected for this subtask

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`  # when overlay-driven compare Blender behavior changes

## Validation Category

- mark-keyed correspondence and validity-retry proof
