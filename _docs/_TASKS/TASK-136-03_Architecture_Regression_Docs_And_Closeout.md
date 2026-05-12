# TASK-136-03: Architecture Regression, Docs, And Closeout

**Status:** ✅ Done
**Priority:** 🔴 High
**Parent:** [TASK-136](./TASK-136_Reference_Guided_Architecture_And_Building_Reconstruction.md)
**Depends On:** [TASK-136-01](./TASK-136-01_Building_Contract_Vocabulary_And_Gate_Templates.md), [TASK-136-02](./TASK-136-02_Guided_Building_Handoff_Search_And_Bounded_Surface.md)
**Objective:** Lock the architecture follow-on slice by extending the existing building owner lanes with architecture-specific regression, Blender-backed proof, and docs that describe the shipped bounded building path accurately.
**Repository Touchpoints:** `server/adapters/mcp/contracts/scene.py`, `server/adapters/mcp/contracts/router.py`, `server/adapters/mcp/guided_naming_policy.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/areas/reference_checkpoint_compare.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/areas/reference_images_runtime.py`, `server/adapters/mcp/areas/reference_silhouette.py`, `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/areas/reference_truth.py`, `server/adapters/mcp/areas/router.py`, `server/application/tool_handlers/router_handler.py`, `server/router/application/workflows/custom/simple_house.yaml`, `server/adapters/mcp/session_capabilities_bootstrap.py`, `server/adapters/mcp/session_capabilities_state.py`, `server/adapters/mcp/session_capabilities_runtime_glue.py`, `tests/unit/adapters/mcp/test_quality_gate_contracts.py`, `tests/unit/adapters/mcp/test_quality_gate_intake.py`, `tests/unit/adapters/mcp/test_quality_gate_verifier.py`, `tests/unit/adapters/mcp/test_guided_mode.py`, `tests/unit/adapters/mcp/test_guided_naming_policy.py`, `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`, `tests/unit/adapters/mcp/test_visibility_policy.py`, `tests/unit/adapters/mcp/test_search_surface.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`, `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`, `tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py`, `tests/unit/router/application/test_router_contracts.py`, `tests/unit/adapters/mcp/test_router_elicitation.py`, `tests/unit/adapters/mcp/test_scene_guided_scope_requirements.py`, `tests/unit/tools/scene/test_scene_contracts.py`, `tests/unit/tools/scene/test_spatial_graph_service.py`, `tests/e2e/router/test_guided_manual_handoff.py`, `tests/e2e/router/test_guided_direct_calls_do_not_trigger_workflows.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/integration/test_guided_search_first_call_tool_boundary.py`, `tests/e2e/integration/test_guided_streamable_spatial_support.py`, `tests/e2e/vision/test_reference_understanding_runtime_surface.py`, `tests/e2e/vision/test_reference_stage_truth_handoff.py`, `tests/e2e/vision/test_reference_stage_silhouette_contract.py`, `tests/e2e/vision/test_reference_stage_multi_reference_scaling.py`, `tests/e2e/vision/test_goal_derived_gate_building_completion.py`, `tests/e2e/vision/test_goal_derived_gate_support_symmetry_surfaces.py`, likely new `_docs/_PROMPTS/REFERENCE_GUIDED_ARCHITECTURE_BUILD.md`, `README.md`, `_docs/_PROMPTS/README.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_ROUTER/README.md`, `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`, `_docs/_VISION/README.md`, `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`, `_docs/AVAILABLE_TOOLS_SUMMARY.md`, `_docs/_TESTS/README.md`, `_docs/_TASKS/README.md`, `_docs/_CHANGELOG/`
**Acceptance Criteria:**
- architecture-specific building blockers survive the current checkpoint, gate, and transport envelopes with typed ids, status reasons, and recommended bounded follow-up tools
- architecture-specific plan/elevation/facade packet evidence survives the
  current `TASK-166` `compare_diagnostics` and compact
  `reference_orchestrator_feedback` projection without a parallel compare path
- the existing building Blender-backed proof lanes are extended with architecture-specific fixtures/assertions rather than duplicated as a new parallel harness
- the shipped building path keeps gate verification, guided flow state, visibility/search shaping, scene-scope discipline, and scene/spatial relation semantics coherent under the extended architecture slice
- public docs and historical change tracking describe the same bounded architecture capability, limitations, and validation evidence

## Implementation Notes

- extend the existing building gate transport/E2E lanes with
  architecture-specific fixtures and assertions instead of planning a second
  parallel harness
- rerun the earlier `TASK-136-02` prompt/provider, router-handoff, search, and
  guided-surface owner lanes as part of closeout instead of narrowing the proof
  pack to only gate/truth suites
- keep the initial runtime proof bounded to shell/opening/roof/support style
  failures, not full procedural building generation
- include a regression proving the architecture handoff uses the explicit
  `reference_guided_architecture_build` recipe and does not silently fall back to
  generic handoff or `simple_house_workflow` for plan/elevation/facade reference
  reconstruction goals
- include packet diagnostics checks when staged compare behavior changes, using
  `tests/unit/adapters/mcp/test_reference_compare_packets.py` and
  `tests/e2e/vision/test_reference_stage_multi_reference_scaling.py`
- update `_docs/_TESTS/README.md` only after the new owner lanes stabilize
- run repo-wide unit and Blender-backed E2E validation outside the sandbox
  before closeout, using the repo-supported commands from `AGENTS.md`

## Completion Summary

Completed on 2026-05-12. This closeout updated the public docs, prompt library,
test strategy, board, and changelog for the architecture path and added
regression coverage for:

- architecture prompt catalog/provider/bridge exposure
- building guided role sequencing and prompt bundles
- architecture guided handoff, search, and visibility shaping
- quality-gate building templates and spatial relation truth
- architecture packet scope labels
- Blender-backed guided handoff and building gate behavior

## Pseudocode

```python
run_unit_owner_lanes_for_building_contract()
run_prompt_and_handoff_owner_lanes_for_guided_surface()
run_transport_lane_for_guided_gate_state_transport()
run_blender_e2e_building_completion_lane()
update_docs_and_board_after_runtime_proof()
```

## Runtime / Security Contract Notes

- proof must use the existing staged reference/gate surfaces and the
  repo-supported Blender-backed E2E path
- packet evidence and compare-budget proof must stay on the closed `TASK-166`
  staged compare owner seams and existing staged response contracts
- do not claim architecture closeout from docs-only edits without matching
  transport and Blender-backed proof

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_quality_gate_contracts.py`
- `tests/unit/adapters/mcp/test_quality_gate_intake.py`
- `tests/unit/adapters/mcp/test_quality_gate_verifier.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_naming_policy.py`
- `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`
- `tests/unit/adapters/mcp/test_prompt_provider.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_reference_compare_packets.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_prompts_bridge.py`
- `tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_scene_guided_scope_requirements.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/scene/test_spatial_graph_service.py`
- `tests/e2e/router/test_guided_manual_handoff.py`
- `tests/e2e/router/test_guided_direct_calls_do_not_trigger_workflows.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/integration/test_guided_search_first_call_tool_boundary.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
- `tests/e2e/vision/test_reference_understanding_runtime_surface.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `tests/e2e/vision/test_reference_stage_silhouette_contract.py`
- `tests/e2e/vision/test_reference_stage_multi_reference_scaling.py`
- `tests/e2e/vision/test_goal_derived_gate_building_completion.py`
- `tests/e2e/vision/test_goal_derived_gate_support_symmetry_surfaces.py`

## Docs To Update

- `README.md`
- `_docs/_PROMPTS/README.md`
- likely new `_docs/_PROMPTS/REFERENCE_GUIDED_ARCHITECTURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_ROUTER/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the first architecture regression pack
  and docs closeout ship.
- Update `_docs/_CHANGELOG/README.md` when that historical entry is added.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_contracts.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py tests/unit/adapters/mcp/test_prompt_provider.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py tests/unit/adapters/mcp/test_scene_guided_scope_requirements.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/scene/test_spatial_graph_service.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py tests/unit/router/application/test_router_contracts.py tests/unit/adapters/mcp/test_router_elicitation.py -q`
- `poetry run pytest ./tests/unit`
- `poetry run pytest tests/e2e/router/test_guided_manual_handoff.py tests/e2e/router/test_guided_direct_calls_do_not_trigger_workflows.py tests/e2e/integration/test_guided_gate_state_transport.py tests/e2e/integration/test_guided_search_first_call_tool_boundary.py tests/e2e/integration/test_guided_streamable_spatial_support.py -q`
- `poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py -q` (adjacent shared guided-surface regression when the architecture slice changes common transport/public-surface behavior)
- `poetry run pre-commit run check-router-tool-metadata --all-files`
- `poetry run pre-commit run --all-files --show-diff-on-failure`
- `poetry run python scripts/run_e2e_tests.py`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_understanding_runtime_surface.py tests/e2e/vision/test_reference_stage_truth_handoff.py tests/e2e/vision/test_reference_stage_silhouette_contract.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_goal_derived_gate_building_completion.py tests/e2e/vision/test_goal_derived_gate_support_symmetry_surfaces.py -q` (supplemental focused Blender-backed lane while iterating; closeout still uses the full repo-supported runner above)

## Status / Board Update

- closed `TASK-136-01`, `TASK-136-02`, `TASK-136-03`, and parent `TASK-136`
  together on 2026-05-12
- moved `TASK-136` from To Do to Done in `_docs/_TASKS/README.md`
- added changelog entry `348-2026-05-12-task-136-architecture-guided-reconstruction.md`
- no direct open child remains under the closed parent; broader future
  architecture generators or module-array macros should be tracked as explicit
  follow-on tasks if/when they become active
