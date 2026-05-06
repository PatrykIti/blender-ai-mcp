# TASK-135-03-03: Refinement Regression Docs And Closeout

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-135-03](./TASK-135-03_Low_Poly_Form_Refinement_Mesh_Window_And_Profile_Macros.md)
**Depends On:** [TASK-135-03-01](./TASK-135-03-01_Refinement_Stage_State_And_Visibility_Gate.md), [TASK-135-03-02](./TASK-135-03-02_Bounded_Profile_Tools_And_Optional_Macro_Wave.md)
**Objective:** Lock the new refinement stage with owner-lane regression, Blender-backed proof, and docs that describe the shipped bounded creature refinement path accurately.
**Repository Touchpoints:** `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/vision/test_goal_derived_gate_creature_completion.py`, `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`, `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_TESTS/README.md`, `_docs/_TASKS/README.md`, `_docs/_CHANGELOG/`
**Acceptance Criteria:** primitive-only creature runs cannot complete past the new refinement gate without the required profile work; transport and checkpoint surfaces describe the same stage/blocker semantics; docs and changelog record the shipped behavior and validation lanes accurately.

## Implementation Notes

- prove the refinement stage on the existing staged checkpoint and gate-transport
  surfaces; do not create a docs-only notion of refinement that the runtime
  never emits
- keep the main creature proof focused on:
  - primitive-only squirrel blocked before final completion
  - required creature seams still visible in truth/follow-up payloads
  - refinement-stage blockers visible on transport-friendly envelopes
- update `_docs/_TESTS/README.md` only after the owner lanes are stable enough to
  document as the current rerun baseline

## Runtime / Security Contract Notes

- transport/runtime proof must use the existing reference/gate surfaces and the
  repo-supported Blender-backed E2E path
- do not claim refinement closeout from docs-only edits without a matching
  regression lane

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/vision/test_goal_derived_gate_creature_completion.py`
- `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`

## Docs To Update

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TESTS/README.md`
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the refinement stage and its proof pack
  are shipped.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_goal_derived_gate_creature_completion.py tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py -q`
