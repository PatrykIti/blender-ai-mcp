# TASK-136-03: Architecture Regression, Docs, And Closeout

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-136](./TASK-136_Reference_Guided_Architecture_And_Building_Reconstruction.md)
**Depends On:** [TASK-136-01](./TASK-136-01_Building_Contract_Vocabulary_And_Gate_Templates.md), [TASK-136-02](./TASK-136-02_Guided_Building_Handoff_Search_And_Bounded_Surface.md)
**Objective:** Lock the architecture follow-on slice by extending the existing building owner lanes with architecture-specific regression, Blender-backed proof, and docs that describe the shipped bounded building path accurately.
**Repository Touchpoints:** `tests/unit/adapters/mcp/test_quality_gate_contracts.py`, `tests/unit/adapters/mcp/test_quality_gate_intake.py`, `tests/unit/adapters/mcp/test_quality_gate_verifier.py`, `tests/unit/adapters/mcp/test_visibility_policy.py`, `tests/unit/adapters/mcp/test_search_surface.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`, `tests/unit/tools/scene/test_scene_contracts.py`, `tests/unit/tools/scene/test_spatial_graph_service.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/vision/test_goal_derived_gate_building_completion.py`, `tests/e2e/vision/test_goal_derived_gate_support_symmetry_surfaces.py`, likely new `_docs/_PROMPTS/REFERENCE_GUIDED_ARCHITECTURE_BUILD.md`, `_docs/_PROMPTS/README.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_TESTS/README.md`, `_docs/_TASKS/README.md`, `_docs/_CHANGELOG/`
**Acceptance Criteria:**
- architecture-specific building blockers survive the current checkpoint, gate, and transport envelopes with typed ids, status reasons, and recommended bounded follow-up tools
- the existing building Blender-backed proof lanes are extended with architecture-specific fixtures/assertions rather than duplicated as a new parallel harness
- unit owner lanes cover gate verification, guided flow state, visibility/search shaping, and scene/spatial relation semantics for the shipped building path
- docs, task statuses, board state, and changelog describe the same bounded architecture capability, limitations, and validation evidence

## Implementation Notes

- extend the existing building gate transport/E2E lanes with
  architecture-specific fixtures and assertions instead of planning a second
  parallel harness
- keep the initial runtime proof bounded to shell/opening/roof/support style
  failures, not full procedural building generation
- update `_docs/_TESTS/README.md` only after the new owner lanes stabilize
- run repo-wide unit and Blender-backed E2E validation outside the sandbox
  before closeout, using the repo-supported commands from `AGENTS.md`

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

- `tests/unit/adapters/mcp/test_quality_gate_contracts.py`
- `tests/unit/adapters/mcp/test_quality_gate_intake.py`
- `tests/unit/adapters/mcp/test_quality_gate_verifier.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/scene/test_spatial_graph_service.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/vision/test_goal_derived_gate_building_completion.py`
- `tests/e2e/vision/test_goal_derived_gate_support_symmetry_surfaces.py`

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
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_contracts.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/scene/test_spatial_graph_service.py -q`
- `poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `poetry run python scripts/run_e2e_tests.py`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_goal_derived_gate_building_completion.py tests/e2e/vision/test_goal_derived_gate_support_symmetry_surfaces.py -q` (supplemental focused Blender-backed lane while iterating; closeout still uses the full repo-supported runner above)

## Status / Board Update

- when this leaf closes, update `TASK-136`, `TASK-136-01`, `TASK-136-02`, and
  `TASK-136-03` statuses together so parent/child state stays synchronized
- update `_docs/_TASKS/README.md` if the umbrella or any explicit follow-on
  changes promoted board state
- if scope remains after umbrella closeout, record it as an explicit follow-on
  task instead of leaving open child drift under a closed parent
