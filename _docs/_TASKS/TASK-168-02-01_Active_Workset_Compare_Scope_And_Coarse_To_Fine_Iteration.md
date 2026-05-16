# TASK-168-02-01: Active Workset Compare Scope And Coarse-To-Fine Iteration

**Status:** ✅ Done
**Priority:** 🔴 High
**Parent:** [TASK-168-02](./TASK-168-02_Typed_Orchestrator_Feedback_Contract_And_Emission_Points.md)
**Objective:** Make staged compare / iterate default to the active fragment, blocker cluster, or focus pair instead of pushing whole-model output into the controller by default.
**Repository Touchpoints:** `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/areas/reference_planner.py`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/contracts/guided_flow.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/e2e/vision/test_reference_stage_multi_reference_scaling.py`, `tests/e2e/vision/test_reference_stage_truth_handoff.py`
**Acceptance Criteria:**
- compare/iterate can resolve one active compare scope from:
  - current guided step
  - current blockers
  - current focus pairs
  - current active workset / last mutation
- the default compare payload targets that scope first instead of the whole assembled model
- the runtime can escalate from local fragment -> larger cluster -> full assembled compare only when needed
- squirrel/controller regressions stop reading huge whole-model outputs for local edits such as tail, ears, or body/head seams

## Implementation Notes

- reuse current substrate instead of inventing a second scope system:
  - `assembled_target_scope`
  - `reference_orchestrator_feedback` and top-level `correction_focus`
  - additive `compare_diagnostics` truth pairs when compact packet diagnostics
    are present
  - scope clusters in `reference_compare_packets.py`
  - `planner_summary.blockers`
  - `refinement_route.target_scope`
- add one explicit resolver, for example:
  - `resolve_active_compare_scope(...)`
- priority should likely be:
  1. unresolved blocker cluster
  2. explicit focus pair
  3. active workset / last mutated object slice
  4. fallback assembled scope
- use coarse-to-fine policy:
  - compact local compare first
  - escalate only if unresolved or ambiguous
- this task is not just “narrow target_object manually”; it should let the
  runtime compute the fragment even when the client is lazy or drifty

## Pseudocode

```python
active_scope = resolve_active_compare_scope(
    guided_flow_state=session.guided_flow_state,
    blockers=planner_summary.blockers,
    focus_pairs=reference_orchestrator_feedback.correction_focus,
    diagnostic_truth_pairs=[
        pair
        for packet in compare_diagnostics.packets
        for pair in packet.truth_pairs
    ],
    last_mutation=current_mutation_hint,
    assembled_target_scope=assembled_target_scope,
)

packets = build_compare_packets_for_scope(active_scope, preset_profile="compact")
if packets.returned_uncertain:
    packets = escalate_compare_scope(active_scope, level="next")
```

## Runtime / Security Contract Notes

- no hidden/internal scope ids in public output
- escalation must remain bounded by existing compare budgets
- local fragment routing must not silently hide required seams from a larger
  active workset; escalation path stays mandatory when blockers cross scopes

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_compare_packets.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/vision/test_reference_stage_multi_reference_scaling.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`

## Docs To Update

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`

## Changelog Impact

- historical closeout entry ownership belongs to
  [TASK-168-04](./TASK-168-04_Profile_Contract_Rewrite_Validation_And_Closeout.md)

## Status / Board Update

- closed administratively under the completed `TASK-168-02` and `TASK-168`
  parents on 2026-05-16
- the final family proof is recorded in
  [TASK-168-04](./TASK-168-04_Profile_Contract_Rewrite_Validation_And_Closeout.md)
  and
  [355. TASK-168 guided registry final drift repair](../_CHANGELOG/355-2026-05-16-task-168-guided-registry-final-drift-repair.md)

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- focused Blender-backed owner lanes covered by the final repo-supported runner:
  - `tests/e2e/vision/test_reference_stage_multi_reference_scaling.py`
  - `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `poetry run python scripts/run_e2e_tests.py`

## Validation Category

- focused reference packet/planner tests plus repo-supported Blender E2E proof
- `git diff --check`
