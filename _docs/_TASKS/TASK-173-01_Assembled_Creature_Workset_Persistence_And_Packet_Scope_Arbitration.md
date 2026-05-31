# TASK-173-01: Assembled Creature Workset Persistence And Packet Scope Arbitration

**Parent:** [TASK-173](./TASK-173_Reference_Guided_Creature_Scope_Convergence_And_Optional_Grounding_Followups.md)
**Status:** ✅ Done
**Priority:** 🔴 High
**Follow-on After:** [TASK-171-02](./TASK-171-02_Active_Workset_Expansion_And_Secondary_Compare_Precedence.md), [TASK-169-02](./TASK-169-02_Global_First_Creature_Compare_Priority_And_Local_Packet_Escalation.md)
**Objective:** Repair the post-refresh creature failure where the assembled workset and packet chooser fall back to the older broad-first `Body + Head` heuristic after secondary-part creation or bounded repairs, instead of correctly rebinding scope and packet precedence for the current assembled creature.
**Repository Touchpoints:** `server/adapters/mcp/session_capabilities_flow.py`, `server/adapters/mcp/session_capabilities_registry.py`, `server/adapters/mcp/session_capabilities_runtime_glue.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/areas/reference_feedback.py`, `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py`
**Acceptance Criteria:**
- newly registered secondary creature parts remain eligible for the active assembled compare workset after mutate/refresh cycles
- packet selection uses one explicit policy when whole-assembly compare and local pair/part compare both look plausible
- a full-creature session cannot repeatedly collapse to `Body + Head` unless the current packet contract explicitly selects that narrower scope

## Implementation Notes

- the latest squirrel run showed the same failure pattern repeatedly even after
  the earlier `TASK-171-02` widening work landed:
  - new ears and legs were created
  - refresh gates were satisfied
  - compare/iterate still returned to an active scope dominated by `Body + Head`
- the remaining bug is not only scope rebind; it is also compare-policy
  precedence between:
  - assembled-scope persistence
  - the older broad-first creature heuristic
  - new blocker/focus state after secondary-part registration
- fix the owner seams rather than masking the issue in prompts:
  - `active_target_scope`
  - packet/workset resolution
  - blocker/focus precedence
  - stale-scope rebind after refresh
- keep broad-first behavior for early unresolved body/head/tail form, but only
  while that is still the dominant unresolved failure class
- once the current session already has registered ears, snout, legs, or tail,
  broad-body/head packets should no longer suppress all appendage-aware packet
  selection by default

## Pseudocode

```python
scope = current_active_scope(state)
scope = merge_registered_roles_into_assembled_scope(scope, guided_part_registry)

packet_candidates = collect_packet_candidates(scope, gate_plan, blocker_state, last_mutation)
if assembled_scope_still_has_primary_shape_priority(packet_candidates):
    selected_scope = assembled_primary_scope(packet_candidates)
elif appendage_or_local_attachment_priority(packet_candidates):
    selected_scope = bounded_local_scope(packet_candidates)
else:
    selected_scope = assembled_scope(packet_candidates)
```

## Runtime / Security Contract Notes

- scope widening must stay bounded to the current guided creature workset; do
  not admit arbitrary scene objects just because they exist
- a rebind after spatial refresh must not silently mark checks as complete for
  a different object set than the one actually inspected
- packet arbitration must remain deterministic and typed; do not fall back to
  prompt-only scope choice

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_reference_compare_packets.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py`

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- board tracking is closed on umbrella `TASK-173`
- no separate promoted board-row change is expected for this subtask unless it
  is later split into a standalone follow-on
- 2026-05-31: completed through the registry-as-compare-scope rewrite. Guided
  registry roles now project into the canonical assembled compare scope, staged
  compare prefers that registered graph before older `Body + Head` name
  heuristics, and diagnostics record whether packet scope came from the registry,
  focus pairs, target scope, or fallback.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_reference_compare_packets.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
- 2026-05-31 focused validation:
  `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py::test_build_compare_packets_prefers_registered_part_graph_over_name_focus_clusters tests/unit/adapters/mcp/test_guided_flow_state_contract.py::test_guided_registry_compare_scope_projects_stable_registered_part_graph -q` -> passed in the focused registry lane

## Validation Category

- guided workset persistence and packet-arbitration proof
