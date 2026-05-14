# TASK-138-03: Character Regression, Docs, And Rig-Handoff Closeout

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-138](./TASK-138_Anatomy_Aware_Reference_Guided_Biped_And_Fantasy_Character_Reconstruction.md)
**Depends On:** [TASK-138-01](./TASK-138-01_Humanoid_Contract_Symmetry_And_Fidelity_Tiers.md), [TASK-138-02](./TASK-138-02_Guided_Character_Flow_Appendage_And_Garment_Boundaries.md)
**Objective:** Lock the first character domain slice with regression, docs, and explicit proof that body reconstruction, appendage/garment handling, and later rig-handoff boundaries are described consistently.
**Repository Touchpoints:** `server/adapters/mcp/contracts/router.py`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/areas/modeling.py`, `server/adapters/mcp/areas/router.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_images_runtime.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/areas/reference_truth.py`, `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/guided_naming_policy.py`, `server/adapters/mcp/router_helper.py`, `server/adapters/mcp/prompts/prompt_catalog.py`, `server/adapters/mcp/prompts/provider.py`, `server/adapters/mcp/prompts/rendering.py`, `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`, `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`, `tests/unit/adapters/mcp/test_guided_naming_policy.py`, `tests/unit/adapters/mcp/test_prompt_catalog.py`, `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`, `tests/unit/adapters/mcp/test_prompt_provider.py`, `tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py`, `tests/unit/adapters/mcp/test_prompts_bridge.py`, `tests/unit/adapters/mcp/test_router_elicitation.py`, `tests/unit/adapters/mcp/test_visibility_policy.py`, `tests/unit/adapters/mcp/test_search_surface.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_public_surface_docs.py`, `tests/unit/router/application/test_router_contracts.py`, `tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py`, `tests/unit/tools/modeling/test_modeling_tools.py`, `tests/e2e/router/test_guided_manual_handoff.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/integration/test_guided_surface_contract_parity.py`, `tests/e2e/integration/test_guided_streamable_spatial_support.py`, `tests/e2e/vision/test_reference_understanding_runtime_surface.py`, `tests/e2e/vision/test_reference_stage_truth_handoff.py`, new `tests/e2e/vision/test_guided_character_reconstruction.py`, `README.md`, likely new `_docs/_PROMPTS/REFERENCE_GUIDED_CHARACTER_BUILD.md`, `_docs/_PROMPTS/README.md`, `_docs/_VISION/README.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`, `_docs/AVAILABLE_TOOLS_SUMMARY.md`, `_docs/_TESTS/README.md`, `_docs/_TASKS/README.md`, `_docs/_CHANGELOG/README.md`
**Acceptance Criteria:** unit owner lanes, router handoff regression, gate-transport regression, and the first bounded character E2E all pass in that order; docs, board state, and changelog keep body-first reconstruction, appendage/garment follow-ons, and later rig-handoff boundaries aligned without implying armature-runtime delivery.

## Implementation Notes

- keep the first regression pack bounded to one or two humanoid/fantasy body
  scenarios
- include explicit checks that garment/armor and later rigging are not treated
  as already solved by the body-first reconstruction slice
- rerun the unit owner lanes before transport, router handoff, and final docs
  closeout; a transport-only pass is not enough for this contract family
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
- keep rig-handoff proof on router/guided/docs surfaces; do not redefine the
  armature MCP runtime as part of this closeout
- keep body reconstruction and rig-handoff guidance separate in the public story

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_naming_policy.py`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`
- `tests/unit/adapters/mcp/test_prompt_provider.py`
- `tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py`
- `tests/unit/adapters/mcp/test_prompts_bridge.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py`
- `tests/unit/tools/modeling/test_modeling_tools.py`
- `tests/e2e/router/test_guided_manual_handoff.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
- `tests/e2e/vision/test_reference_understanding_runtime_surface.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- new `tests/e2e/vision/test_guided_character_reconstruction.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`

## Docs To Update

- likely new `_docs/_PROMPTS/REFERENCE_GUIDED_CHARACTER_BUILD.md`
- `README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_VISION/README.md`
- `_docs/_ROUTER/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/_ROUTER/TOOLS/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the first character regression/docs
  closeout ships.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_guided_naming_policy.py tests/unit/adapters/mcp/test_prompt_catalog.py tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py tests/unit/adapters/mcp/test_prompt_provider.py tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py tests/unit/adapters/mcp/test_prompts_bridge.py tests/unit/adapters/mcp/test_router_elicitation.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/router/application/test_router_contracts.py tests/unit/tools/modeling/test_modeling_tools.py -q`
- `Outside sandbox before closeout: poetry run pytest ./tests/unit`
- `PYTHONPATH=. poetry run pytest tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py -q`
- `Supplemental focused lane while iterating: poetry run pytest tests/e2e/router/test_guided_manual_handoff.py -q`
- `Supplemental focused lane while iterating: poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `Supplemental focused lane while iterating: poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py -q`
- `Supplemental focused lane while iterating: poetry run pytest tests/e2e/integration/test_guided_streamable_spatial_support.py -q`
- `Supplemental focused lane while iterating: PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_understanding_runtime_surface.py tests/e2e/vision/test_reference_stage_truth_handoff.py -q`
- `Supplemental future dedicated character lane once the file exists: PYTHONPATH=. poetry run pytest tests/e2e/vision/test_guided_character_reconstruction.py -q`
- `Outside sandbox before closeout: poetry run python scripts/run_e2e_tests.py`

## Status / Board Update

- close `TASK-138-03` and the `TASK-138` umbrella only after the unit owner
  lanes, router handoff regression, transport regression, and character E2E
  proof land together with the docs/changelog updates
- if later work needs real armature runtime or `server/adapters/mcp/areas/armature.py`
  changes, track that as a separate follow-on instead of widening this
  body-first family during closeout
- any such descendant should be promoted as a standalone `Follow-on After:
  TASK-138` task, not reopened under `TASK-138-03` or folded back into this
  body-first family
