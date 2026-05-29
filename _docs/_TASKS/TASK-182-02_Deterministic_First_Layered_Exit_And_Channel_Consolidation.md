# TASK-182-02: Deterministic-First Layered Exit And Channel Consolidation

**Parent:** [TASK-182](./TASK-182_Critic_Verify_Compare_Loop_And_Deterministic_Exit_Criteria.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Follow-on After:** [TASK-182-01](./TASK-182-01_Critic_Verify_Split_With_Stable_Defect_Identifiers.md), [TASK-157-02](./TASK-157-02_Deterministic_Gate_Verifier_And_Status_Model.md)
**Objective:** Formalize a layered exit where a hard non-VLM gate (registry part-count match AND required contacts via the deterministic verifier) is consulted first, the VLM verdict is used only as a tiebreaker, every claim is provenance-tagged, and the 4-6 overlapping recommendation/correction channels collapse into one ranked `authoritative_next_actions` field.

**Repository Touchpoints:** `server/adapters/mcp/areas/reference_planner.py`, `server/adapters/mcp/transforms/quality_gate_verifier.py`, `server/adapters/mcp/sampling/result_types.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/contracts/quality_gates.py`, `tests/unit/adapters/mcp/test_quality_gate_verifier.py`, `tests/e2e/vision/test_goal_derived_gate_creature_completion.py`

**Acceptance Criteria:**
- the exit decision is layered and ordered: the hard non-VLM gate
  (`verify_gate_plan_with_relation_graph(...)` — registry part-count match via
  the required-part verifier AND required contacts via the attachment/support
  verifiers) is consulted first; the VLM verdict is consulted only to break ties
  between otherwise-equal deterministic outcomes
- a scope gate cannot advance while its required part-count or contact gate is
  `failed`/`blocked`, regardless of any VLM `resolved` verdict
- every surfaced compare/feedback claim is provenance-tagged with its source
  class (`scene_truth` / `mesh_metric` / `spatial_relation` / advisory `vision`)
- the orchestrator read model exposes one ranked `authoritative_next_actions`
  field; the previously parallel `next_actions`, `recommended_support_tools`,
  `recommended_repair`, and `correction_focus` channels feed it with preserved
  provenance instead of competing as equal lists
- ranking is deterministic and explainable: deterministic-blocker-derived
  actions outrank advisory vision-derived actions, ties broken by a stable key

## Implementation Notes

- This implements the **deterministic-first layered metric ordering** from
  **IR3D-Bench (arXiv:2506.23329)**, which scores reconstruction by checking
  deterministic structure first and using the VLM judge only where deterministic
  metrics are silent or tied; and the **iterative replanning** discipline from
  **SayPlan (arXiv:2307.06135)**, where the planner re-derives a single next
  action from verified state rather than from a bag of parallel suggestions.
- The hard gate already exists. `verify_gate_plan_with_relation_graph(...)`
  (`transforms/quality_gate_verifier.py:22`) is authoritative: required-part
  count matching runs in `_verify_required_part_gate(...)` (`:131`), required
  contacts run in `_verify_attachment_gate(...)` (`:183`) and
  `_verify_support_gate(...)` (`:250`), and `_apply_final_completion_status(...)`
  (`:386`) already blocks final completion while any required non-final gate is
  `pending`/`blocked`/`failed`/`stale`. The layered exit must call this *first*
  and treat the VLM verdict (the `verify_status` from TASK-182-01) only as a
  tiebreaker, never as an override.
- The overlapping channels to collapse all already exist in one place:
  `build_reference_orchestrator_feedback(...)` (`areas/reference_feedback.py:384`)
  currently emits `next_actions`, `recommended_support_tools`,
  `recommended_repair`, `correction_focus`, `evidence_summary`, and
  `uncertainty_notes` as parallel fields, fed from:
  - planner blockers / route reason via
    `select_refinement_route(...)` (`areas/reference_planner.py:623`) and
    `_support_tools_from_blockers(...)` (`:538`)
  - gate completion blockers via `_gate_plan_completion_blockers(...)` (`:559`)
  - packet correction focus / evidence via `compare_diagnostics`
  - advisory vision prose via the merged `VisionAssistContract`
  - runtime policy block strings
  This subtask adds one ranked `authoritative_next_actions` projection on
  `ReferenceOrchestratorFeedbackContract` (`contracts/reference.py:336`) that
  draws from those same sources but assigns each action a provenance tag and a
  deterministic rank, so the orchestrator reads one ordered list instead of
  guessing precedence across six.
- Provenance tagging should reuse the existing source-class vocabulary already
  used by the gate verifier evidence (`scene_truth`, `spatial_relation`,
  `mesh_metric` in `GateEvidenceRefContract`) and the planner provenance
  (`ReferencePlannerEvidenceSourceContract` source classes from
  `_planner_provenance(...)`, `areas/reference_planner.py:450`). Advisory vision
  actions carry the `vision` source class so they are visibly lower-authority.
- Confidence handling: the merged compare `confidence` is non-authoritative and
  is currently not range-validated; the tiebreaker must not promote a VLM verdict
  above a deterministic outcome on confidence alone, and any out-of-range
  confidence must not silently win.
- Keep the change additive and typed. The single ranked field is added next to
  the existing channels (which can remain for backward-compatible detail) rather
  than deleting them outright, so existing consumers and parity tests stay green;
  the orchestrator-facing guidance documents `authoritative_next_actions` as the
  field to follow.

## Pseudocode

```python
def layered_exit_decision(scope_label, gate_plan, verify_statuses, vlm_verdict):
    # Layer 1: hard non-VLM gate (registry part-count AND required contacts)
    hard = verify_gate_plan_with_relation_graph(gate_plan, relation_graph)
    scope_gates = gates_for_scope(hard, scope_label)
    if any(g.status in {"failed", "blocked", "stale"} for g in scope_gates if g.required):
        return Exit(advance=False, source="scene_truth", reason="required gate not passed")

    # all hard gates pass -> require verified-resolved defects (from TASK-182-01)
    if not all_open_defects_resolved_or_downgraded(scope_label, verify_statuses):
        return Exit(advance=False, source="vision", reason="open defects unverified")

    # Layer 2: VLM verdict only as tiebreaker between equal deterministic outcomes
    if deterministic_outcomes_tied(scope_gates):
        return Exit(advance=vlm_verdict.prefers_advance, source="vision_tiebreaker")
    return Exit(advance=True, source="scene_truth")


def authoritative_next_actions(planner, gate_blockers, packet_focus, vision_focus):
    ranked: list[RankedAction] = []
    for b in gate_blockers:        # deterministic, highest authority
        ranked.append(RankedAction(b.message, source="scene_truth", rank_key=(0, b.gate_id)))
    for b in planner.blockers:     # deterministic route blockers
        ranked.append(RankedAction(b.reason, source=b.source_class, rank_key=(1, b.blocker_id)))
    for f in packet_focus:         # packeted compare focus
        ranked.append(RankedAction(f, source="mesh_metric_or_relation", rank_key=(2, f)))
    for f in vision_focus:         # advisory vision prose, lowest authority
        ranked.append(RankedAction(f, source="vision", rank_key=(3, normalize(f))))
    return dedupe_stable(sorted(ranked, key=lambda a: a.rank_key))
```

## Runtime / Security Contract Notes

- vision stays ADVISORY: the VLM verdict is only a tiebreaker between equal
  deterministic outcomes and can never advance a gate that the deterministic
  verifier did not pass; new fields keep `not_truth_source` /
  `requires_deterministic_checks_for_correctness`
- the deterministic verifier (`scene_relation_graph` evidence,
  `scene_assert_contact` / `measure`) owns scene truth; vision must not mark
  gates complete or unlock tools
- magnitudes surfaced in actions are proportional ratios versus a trusted
  reference anchor, never authoritative absolute measurements
- actions and evidence stay symbolic with explicit provenance; no raw coordinate
  tokens as primary evidence and no VLM-side chain-of-thought — ranking and
  reasoning stay in the orchestrator
- the layered exit must remain fail-closed: if deterministic evidence is missing
  or stale, prefer a bounded re-check over a false "advance"

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_quality_gate_verifier.py`
- `tests/e2e/vision/test_goal_derived_gate_creature_completion.py`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_VISION/HYBRID_LOOP_REAL_CREATURE_EVAL.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- board tracking remains on umbrella `TASK-182`
- no separate promoted board-row change is expected for this subtask unless it
  later becomes a standalone follow-on

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_verifier.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_goal_derived_gate_creature_completion.py -q`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`

## Validation Category

- deterministic-first exit ordering and channel-consolidation proof
