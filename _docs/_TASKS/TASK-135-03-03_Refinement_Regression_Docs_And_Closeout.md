# TASK-135-03-03: Refinement Regression Docs And Closeout

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-135-03](./TASK-135-03_Low_Poly_Form_Refinement_Mesh_Window_And_Profile_Macros.md)
**Depends On:** [TASK-135-03-01](./TASK-135-03-01_Refinement_Stage_State_And_Visibility_Gate.md), [TASK-135-03-02](./TASK-135-03-02_Bounded_Profile_Tools_And_Optional_Macro_Wave.md)
**Objective:** Lock the new refinement stage with owner-lane regression, Blender-backed proof, and docs that describe the shipped bounded creature refinement path accurately.
**Repository Touchpoints:** `server/adapters/mcp/areas/reference.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/unit/adapters/mcp/test_guided_mode.py`, `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`, `tests/unit/adapters/mcp/test_public_surface_docs.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/vision/test_goal_derived_gate_creature_completion.py`, `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`, `tests/e2e/vision/test_reference_stage_truth_handoff.py`, `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_TESTS/README.md`, `_docs/_TASKS/README.md`, `_docs/_CHANGELOG/`
**Acceptance Criteria:** primitive-only creature runs cannot complete past the new refinement gate without the required profile work; transport and checkpoint surfaces describe the same stage/blocker semantics; docs and changelog record the shipped behavior and validation lanes accurately.

## Implementation Notes

- prove the refinement stage on the existing staged checkpoint and gate-transport
  surfaces; do not create a docs-only notion of refinement that the runtime
  never emits
- keep the main creature proof focused on:
  - primitive-only squirrel blocked before final completion
  - required creature seams still visible in truth/follow-up payloads
  - refinement-stage blockers visible on transport-friendly envelopes
- keep the existing `refinement_route` / `refinement_handoff` checkpoint surfaces
  in the proof pack so the explicit creature refinement step does not drift
  from the shipped planner baseline
- update `_docs/_TESTS/README.md` only after the owner lanes are stable enough to
  document as the current rerun baseline

## Runtime / Security Contract Notes

- Visibility level: transport/runtime proof must use the existing public
  reference/gate surfaces, including `guided_flow_state`, `active_gate_plan`,
  `refinement_route`, and `refinement_handoff`; do not close this task from a
  docs-only notion of refinement.
- Read-only vs mutating behavior: closeout proof may read session/checkpoint
  envelopes, but any repair or refinement behavior still relies on the existing
  mutating modeling, mesh, scene, and macro surfaces.
- Mode and selection impact: Blender-backed proof must confirm that refinement
  steps and follow-on repairs do not leave sessions stranded in the wrong mode
  or selection state.
- Session and auth assumptions: validation must cover the repo-supported stdio /
  Streamable HTTP session path plus the local Blender RPC-backed runtime
  surface; session state must remain isolated per request flow.
- Parameter validation and compatibility: closeout should confirm strict
  response-contract parity for new step names, blockers, and route/handoff
  fields, with explicit compatibility behavior where relevant.
- Side effects, recovery, and logging: do not claim refinement closeout without
  a matching regression lane. Keep logs and proof artifacts free of provider
  keys, raw local paths, or unredacted vision payloads.

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/vision/test_goal_derived_gate_creature_completion.py`
- `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`

## Docs To Update

- `README.md`
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
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_guided_surface_benchmarks.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_goal_derived_gate_creature_completion.py tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py tests/e2e/vision/test_reference_stage_truth_handoff.py -q`
- `Outside sandbox before closeout: PYTHONPATH=. poetry run pytest ./tests/unit`
- `Outside sandbox for Blender-backed runtime proof: poetry run python scripts/run_e2e_tests.py`
