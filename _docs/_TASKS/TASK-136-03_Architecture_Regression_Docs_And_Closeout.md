# TASK-136-03: Architecture Regression, Docs, And Closeout

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-136](./TASK-136_Reference_Guided_Architecture_And_Building_Reconstruction.md)
**Depends On:** [TASK-136-01](./TASK-136-01_Building_Contract_Vocabulary_And_Gate_Templates.md), [TASK-136-02](./TASK-136-02_Guided_Building_Handoff_Search_And_Bounded_Surface.md)
**Objective:** Lock the first architecture domain slice with owner-lane regression, Blender-backed proof, and docs that describe the shipped bounded building path accurately.
**Repository Touchpoints:** `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/vision/test_goal_derived_gate_building_completion.py`, `_docs/_PROMPTS/DEMO_TASK_LOW_POLY_MEDIEVAL_WELL.md`, likely new `_docs/_PROMPTS/REFERENCE_GUIDED_ARCHITECTURE_BUILD.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_TESTS/README.md`, `_docs/_TASKS/README.md`, `_docs/_CHANGELOG/`
**Acceptance Criteria:** building-stage blockers survive transport and staged checkpoint surfaces; the Blender-backed building lane proves the bounded architecture path; docs and changelog match the shipped capability and limitations.

## Implementation Notes

- prove the first architecture slice on the existing building gate E2E lane
- keep the initial runtime proof bounded to shell/opening/roof/support style
  failures, not full procedural building generation
- update `_docs/_TESTS/README.md` only after the new owner lanes stabilize

## Pseudocode

```python
run_unit_owner_lanes_for_building_contract()
run_transport_lane_for_guided_gate_state_transport()
run_blender_e2e_building_completion_lane()
update_docs_and_board_after_runtime_proof()
```

## Runtime / Security Contract Notes

- proof must use the existing staged reference/gate surfaces and the
  repo-supported Blender-backed E2E path
- do not claim architecture closeout from docs-only edits without matching
  transport and Blender-backed proof

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/vision/test_goal_derived_gate_building_completion.py`

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TESTS/README.md`
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the first architecture regression pack
  and docs closeout ship.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_goal_derived_gate_building_completion.py -q`
