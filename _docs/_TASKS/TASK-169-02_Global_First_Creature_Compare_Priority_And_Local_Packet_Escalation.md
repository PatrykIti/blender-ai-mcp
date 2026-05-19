# TASK-169-02: Global-First Creature Compare Priority And Local Packet Escalation

**Parent:** [TASK-169](./TASK-169_Reference_Guided_Quality_Drift_Regression_And_Runtime_Authority.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Keep early creature compare global enough to fix body/head/tail silhouette before the loop collapses into limb-, ear-, or seam-local packets.
**Repository Touchpoints:** `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/areas/reference_planner.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/contracts/reference.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/e2e/vision/test_reference_stage_multi_reference_scaling.py`, `tests/e2e/vision/test_reference_stage_truth_handoff.py`
**Acceptance Criteria:**
- early creature form-finding can prefer a broad body/head/tail or whole-workset compare before descending into local blocker packets
- packet-local compare remains bounded and available, but no longer dominates while the global creature silhouette is still obviously wrong
- the current compact feedback surfaces can explain when the runtime intentionally stayed broad and when it later narrowed to local packets

## Implementation Notes

- preserve the `TASK-166` / `TASK-168` packet strategy; do not undo local
  packeting globally
- add one creature-aware guard on top of the existing substrate:
  - `resolve_active_compare_scope(...)`
  - staged packet builders/schedulers
  - truth-followup focus pairs
  - `reference_orchestrator_feedback`
  - `local_region_hint`
- the current runtime priority is blocker cluster -> focus pair -> last
  mutation -> active workset; this slice should only override that order where
  a creature run is still failing at the broad silhouette stage
- the likely priority for common quadruped runs should become:
  1. broad primary-mass silhouette checkpoint when body/head/tail are still the
     main unresolved form
  2. blocker cluster / focus pair when the coarse silhouette is already viable
  3. last mutation / local seam repair when the run is clearly in later cleanup
- use runtime-owned evidence for this decision, not prompt-only prose

## Pseudocode

```python
scope = resolve_active_compare_scope(...)
if domain_profile == "creature" and coarse_silhouette_still_unresolved(scope, gate_plan, truth_followup):
    scope = promote_to_primary_mass_workset(scope)

packets = build_compare_packets_for_scope(scope, preset_profile="compact")
if packets.returned_uncertain:
    packets = escalate_compare_scope(scope, level="next")
```

## Runtime / Security Contract Notes

- broad-first compare must stay bounded by the existing packet/budget policy
- the runtime must not hide required seams forever behind a permanently broad
  compare; local escalation remains mandatory after the broad checkpoint passes
- compact controller payloads should explain the broad-first choice without
  dumping raw packet internals by default
- packet changes must stay aligned with the current
  `reference_compare_stage_checkpoint(...)` contract instead of inventing a
  second public packet surface

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

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- keep nested under `TASK-169`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_stage_multi_reference_scaling.py tests/e2e/vision/test_reference_stage_truth_handoff.py -q`

## Validation Category

- reference packet/planner and guided vision/runtime proof
