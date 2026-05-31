# TASK-182-01: Critic/Verify Split With Stable Defect Identifiers

**Parent:** [TASK-182](./TASK-182_Critic_Verify_Compare_Loop_And_Deterministic_Exit_Criteria.md)
**Status:** 🚧 In Progress
**Progress:** Stable defect-ID substrate shipped via changelog 373, but the audit confirmed the full Critic/Verify split is not complete. Remaining work: explicit `open_defects` / `verify_status` round-trip, rerendering the same packet views during Verify, and deterministic verifier checks before a defect is treated as closed.
**Priority:** 🔴 High
**Follow-on After:** [TASK-166-02](./TASK-166-02_Truth_First_Two_Pass_Compare_Execution.md), [TASK-178-01](./TASK-178-01_Structured_Vision_Finding_Contract_Model.md)
**Objective:** Split compare into a Critic pass that emits defects with stable IDs and a Verify pass that re-renders the same views and checks off each open defect, so a scope gate only advances when its scope defects are verified-resolved or explicitly downgraded — vision stays advisory throughout.

**Repository Touchpoints:** `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/sampling/result_types.py`, `server/adapters/mcp/contracts/reference.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/e2e/integration/test_guided_inspect_validate_handoff.py`

**Acceptance Criteria:**
- the Critic pass emits zero or more defects per packet, each with a stable
  defect ID derived deterministically from packet identity + defect content (so
  the same defect re-derives the same ID across cycles), plus a scope/relation
  reference and an advisory severity
- the Verify pass re-renders the *same* packet views (same `target_view` and
  `capture_labels` from `ReferenceComparePacketContract`) and reports each open
  defect ID as `resolved`, `unresolved`, or `downgraded`, with a recorded reason
  for any downgrade
- a defect is only treated as closed when the Verify pass observed the same
  views and the deterministic gate authority did not re-fail the corresponding
  scope; an optimistic "looks better" re-render alone does not close it
- the per-defect verify status is carried additively on the existing packet and
  diagnostics contracts without forking the packet model, and all new fields
  keep `not_truth_source` / `requires_deterministic_checks_for_correctness`
- defect IDs round-trip through `synthesize_packet_vision_result(...)` so synthesis
  preserves which prior defects each packet closed instead of flattening to prose

## Implementation Notes

- This implements the **Critic/Verify** decomposition from **LL3M
  (arXiv:2508.08228)**, whose Critic/Verification split re-checks each prior
  defect after an edit rather than re-describing the whole subject (the paper
  reports a substantial one-pass edit-resolution gain from this split — an
  upstream synthetic result, to be re-measured on `tests/fixtures/vision_eval`
  before any gain is claimed here). The repo currently has only the "describe"
  half: `build_compare_packets(...)`
  (`areas/reference_compare_packets.py:1016`) plans packets,
  `merge_packet_phase_results(...)` (`:1213`) merges extraction + ranking, and
  `synthesize_packet_vision_result(...)` (`:1258`) flattens everything into
  `VisionAssistContract` lists. None of these re-render to confirm a prior
  defect closed.
- Stable defect identity should reuse the existing deterministic ID approach in
  this module. `_stable_packet_id(prefix, *parts)`
  (`areas/reference_compare_packets.py:181`) already builds reproducible
  `prefix:slug:sha1` IDs from normalized parts; a sibling `_stable_defect_id(...)`
  should derive a defect ID from the packet ID plus the normalized defect text /
  relation reference so the same defect re-derives the same ID on retry. This
  matches the existing guarantee proved by
  `test_build_compare_packets_reuses_stable_packet_ids_for_equivalent_retry_inputs`.
- The Critic defect list and the Verify per-defect status are *advisory*. The
  authoritative close signal still comes from the deterministic verifier
  (`transforms/quality_gate_verifier.py`), owned by TASK-182-02; this subtask
  only ensures the loop has a stable handle (the defect ID) to check off and a
  contract slot to record `resolved`/`unresolved`/`downgraded`.
- Carry the new fields additively:
  - on `ReferenceComparePacketContract` (`contracts/reference.py:532`), which
    already holds `correction_focus`, `evidence_summary`, and
    `uncertainty_notes`, add an `open_defects` list (defect ID + summary +
    scope/relation ref + advisory severity) and a `verify_status` list
    (defect ID + `resolved`/`unresolved`/`downgraded` + reason)
  - on `VisionAssistContract` (`sampling/result_types.py:149`), add the
    parallel typed fields so the synthesized result keeps defect identity; keep
    `boundary_policy` (`VisionBoundaryPolicyContract`, `:115`) enforced
  - `build_reference_orchestrator_feedback(...)`
    (`areas/reference_feedback.py:384`) should surface unresolved defect IDs in
    `uncertainty_notes` so the orchestrator sees what is still open, but must not
    treat any verify status as a gate-complete signal
- Verify must re-render the *same* views. The packet already pins
  `target_view`, `capture_labels`, and `reference_ids`; the Verify pass must not
  silently swap framing, because a different view re-renders a different
  observation and cannot legitimately close a defect raised on the original
  view.
- Magnitudes inside defect summaries stay proportional ratios versus a trusted
  reference anchor, never absolute measurements; defect text stays symbolic
  (relation + ratio), not raw coordinate tokens.

## Pseudocode

```python
def critic_pass(packet, vision_result) -> list[OpenDefect]:
    defects: list[OpenDefect] = []
    for item in iter_packet_findings(vision_result):  # correction_focus + shape/proportion
        defect_id = _stable_defect_id(packet.packet_id, item.relation_ref, item.summary)
        defects.append(
            OpenDefect(
                defect_id=defect_id,
                summary=item.summary,                  # symbolic + proportional ratio only
                scope_label=packet.scope_label,
                relation_ref=item.relation_ref,
                severity=item.severity,                # advisory
            )
        )
    return defects  # advisory; not a gate signal


def verify_pass(packet, open_defects, rerender_result, gate_authority) -> list[VerifyStatus]:
    # rerender_result MUST come from re-rendering packet.target_view / capture_labels
    assert rerender_result.views == packet.capture_labels
    statuses: list[VerifyStatus] = []
    for defect in open_defects:
        scope_still_failing = gate_authority.scope_failed(defect.scope_label, defect.relation_ref)
        looks_resolved = rerender_observes_resolution(rerender_result, defect)
        if scope_still_failing:
            statuses.append(VerifyStatus(defect.defect_id, "unresolved", reason="gate still failing"))
        elif looks_resolved:
            statuses.append(VerifyStatus(defect.defect_id, "resolved", reason=None))
        else:
            statuses.append(VerifyStatus(defect.defect_id, "unresolved", reason="not observed in re-render"))
    return statuses


def can_advance_scope(scope_label, statuses) -> bool:
    open_for_scope = [s for s in statuses if s.scope_label == scope_label]
    return all(s.state in {"resolved", "downgraded"} for s in open_for_scope)
```

## Runtime / Security Contract Notes

- vision stays ADVISORY: `open_defects` and `verify_status` are VLM
  interpretation and keep `not_truth_source` /
  `requires_deterministic_checks_for_correctness`; they must never mark a gate
  complete or unlock a tool
- a Verify `resolved` status is necessary but not sufficient for advancing a
  gate; the deterministic verifier (TASK-182-02) is the hard authority
- any magnitude in a defect summary is a proportional ratio versus a trusted
  reference anchor, never an authoritative absolute measurement
- defect summaries stay symbolic (relation + ratio); no raw coordinate tokens as
  primary evidence and no VLM-side chain-of-thought for spatial judgments
- heavier perception sidecars stay default-off, advisory-only, and
  packet-bounded; this subtask does not change the `TASK-172` activation seam

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_compare_packets.py`
- `tests/e2e/integration/test_guided_inspect_validate_handoff.py`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- board tracking remains on umbrella `TASK-182`
- no separate promoted board-row change is expected for this subtask unless it
  later becomes a standalone follow-on

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_inspect_validate_handoff.py -q`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`

## Validation Category

- critic/verify defect round-trip and advisory-boundary proof
