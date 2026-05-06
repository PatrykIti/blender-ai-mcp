# TASK-138-03: Character Regression, Docs, And Rig-Handoff Closeout

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-138](./TASK-138_Anatomy_Aware_Reference_Guided_Biped_And_Fantasy_Character_Reconstruction.md)
**Depends On:** [TASK-138-01](./TASK-138-01_Humanoid_Contract_Symmetry_And_Fidelity_Tiers.md), [TASK-138-02](./TASK-138-02_Guided_Character_Flow_Appendage_And_Garment_Boundaries.md)
**Objective:** Lock the first character domain slice with regression, docs, and explicit proof that body reconstruction, appendage/garment handling, and later rig-handoff boundaries are described consistently.
**Repository Touchpoints:** new `tests/e2e/vision/test_guided_character_reconstruction.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, likely new `_docs/_PROMPTS/REFERENCE_GUIDED_CHARACTER_BUILD.md`, `_docs/_VISION/README.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_TESTS/README.md`, `_docs/_TASKS/README.md`, `_docs/_CHANGELOG/`
**Acceptance Criteria:** this leaf creates the first dedicated character E2E lane proving staged body-first blockers on the live transport surface; docs and changelog keep rig-handoff and garment/appendage boundaries explicit; operator guidance does not overclaim existing character support.

## Implementation Notes

- keep the first regression pack bounded to one or two humanoid/fantasy body
  scenarios
- include explicit checks that garment/armor and later rigging are not treated
  as already solved by the body-first reconstruction slice
- this leaf owns creating the first dedicated
  `tests/e2e/vision/test_guided_character_reconstruction.py` proof lane instead
  of relying only on generic transport coverage
- update board/tests docs only after the owner lanes are stable enough to
  document as current rerun guidance

## Pseudocode

```python
run_unit_owner_lanes_for_character_contract()
run_transport_lane_for_staged_gate_reporting()
run_first_bounded_character_e2e_lane()
verify_docs_keep_rig_handoff_separate_from_body_reconstruction()
```

## Runtime / Security Contract Notes

- do not close this slice from docs-only edits without matching transport/runtime
  proof
- keep body reconstruction and rig-handoff guidance separate in the public story

## Tests To Add/Update

- new `tests/e2e/vision/test_guided_character_reconstruction.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`

## Docs To Update

- likely new `_docs/_PROMPTS/REFERENCE_GUIDED_CHARACTER_BUILD.md`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TESTS/README.md`
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the first character regression/docs
  closeout ships.

## Validation Commands

- `git diff --check`
- `poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_guided_character_reconstruction.py -q`
