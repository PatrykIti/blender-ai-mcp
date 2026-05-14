# TASK-137-02: Guided Organ Loop, Relation Semantics, And Bounded Surface

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-137](./TASK-137_Anatomy_Aware_Reference_Guided_Organ_Reconstruction.md)
**Depends On:** [TASK-137-01](./TASK-137-01_Organ_Domain_Boundary_Vocabulary_And_Fidelity_Tiers.md), [TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md), [TASK-158](./TASK-158_Vision_And_Creature_Gate_Boundary_Doc_Alignment.md), [TASK-163](./TASK-163_Vision_Orchestrator_Feedback_Strategy_Normalization_And_Optional_Perception_Adapters.md)
**Objective:** Turn the organ contract into a usable guided path with staged organ loops, organ-specific relation semantics, and a bounded modeling/sculpt/lattice surface on the existing guided-domain substrate, with one explicit public guided-state contract for organ sessions.
**Repository Touchpoints:** `server/adapters/mcp/contracts/guided_flow.py`, `server/adapters/mcp/contracts/router.py`, `server/adapters/mcp/contracts/scene.py`, `server/adapters/mcp/contracts/quality_gates.py`, `server/adapters/mcp/session_capabilities.py`, `server/adapters/mcp/session_capabilities_bootstrap.py`, `server/adapters/mcp/session_capabilities_registry.py`, `server/adapters/mcp/session_capabilities_state.py`, `server/adapters/mcp/session_capabilities_flow.py`, `server/adapters/mcp/session_capabilities_runtime_glue.py`, `server/adapters/mcp/guided_mode.py`, `server/adapters/mcp/guided_naming_policy.py`, `server/adapters/mcp/router_helper.py`, `server/adapters/mcp/prompts/prompt_catalog.py`, `server/adapters/mcp/transforms/visibility_policy.py`, `server/adapters/mcp/transforms/quality_gate_verifier.py`, `server/adapters/mcp/discovery/search_surface.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/areas/reference_images_runtime.py`, `server/adapters/mcp/areas/reference_planner.py`, `server/adapters/mcp/areas/router.py`, `server/adapters/mcp/areas/modeling.py`, `server/adapters/mcp/areas/mesh.py`, `server/adapters/mcp/areas/sculpt.py`, `server/adapters/mcp/areas/lattice.py`, `server/application/services/spatial_graph.py`, `server/router/infrastructure/tools_metadata/_schema.json`, `server/router/infrastructure/tools_metadata/scene/scene_relation_graph.json`, `server/router/infrastructure/tools_metadata/modeling/modeling_create_primitive.json`, `server/router/infrastructure/tools_metadata/reference/reference_images.json`, `server/router/infrastructure/tools_metadata/reference/reference_compare_stage_checkpoint.json`, `server/router/infrastructure/tools_metadata/reference/reference_iterate_stage_checkpoint.json`, `server/router/infrastructure/tools_metadata/mesh/`, `server/router/infrastructure/tools_metadata/sculpt/`, `server/router/infrastructure/tools_metadata/lattice/`, `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`, `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`, `tests/unit/adapters/mcp/test_guided_mode.py`, `tests/unit/adapters/mcp/test_guided_naming_policy.py`, `tests/unit/adapters/mcp/test_visibility_policy.py`, `tests/unit/adapters/mcp/test_search_surface.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_router_elicitation.py`, `tests/unit/adapters/mcp/test_context_bridge.py`, `tests/unit/adapters/mcp/test_prompt_catalog.py`, `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`, `tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py`, `tests/unit/adapters/mcp/test_quality_gate_contracts.py`, `tests/unit/adapters/mcp/test_quality_gate_intake.py`, `tests/unit/adapters/mcp/test_quality_gate_verifier.py`, `tests/unit/router/application/test_router_contracts.py`, `tests/unit/router/infrastructure/test_metadata_loader.py`, `tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py`, `tests/unit/tools/scene/test_scene_contracts.py`, `tests/unit/tools/scene/test_spatial_graph_service.py`, `tests/unit/tools/modeling/test_modeling_tools.py`, `tests/unit/tools/mesh/test_mesh_organic.py`, `tests/unit/tools/sculpt/test_sculpt_tools.py`, `tests/unit/tools/lattice/test_lattice_handler.py`, `tests/e2e/router/test_guided_manual_handoff.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/integration/test_guided_surface_contract_parity.py`, `tests/e2e/integration/test_mcp_transport_modes.py`, likely new `tests/e2e/vision/test_guided_organ_reconstruction.py`
**Acceptance Criteria:** organ work can move through bounded stages such as primary mass, lobe/chamber definition, cavity/port landmarks, and final validation; relation semantics are planned and verified through the current scene/spatial/gate substrate; the public surface stays bounded on the existing reference/router/checkpoint transport and does not collapse into unrestricted sculpt.

## Implementation Notes

- stage organ work explicitly instead of treating it as generic organic blob
  sculpting
- distinguish fused, embedded, attached, and paired relations in the staged
  loop and correction policy
- keep sculpt, lattice, and modeling families bounded and role-aware
- preserve the current session-state and gate-transport model
- keep staged organ blockers and loop-facing summaries on the existing
  `reference.py` / `reference_feedback.py` delivery seams instead of inventing a
  second organ-only reporting surface
- use one explicit public guided-state contract for organ sessions:
  `domain_profile="organ"` when this leaf promotes a dedicated organ flow; if
  any internal overlay helper remains, it should derive bounded behavior inside
  that declared profile rather than splitting the public contract between
  profile and overlay
- update `contracts/guided_flow.py`, `guided_naming_policy.py`,
  `router_helper.py`, router/profile selection, and prompt-bundle mapping
  together; do not hide a one-off `domain_profile == "organ"` branch only in
  `session_capabilities_flow.py`
- extend the repo-owned gate-template seam in
  `server/adapters/mcp/contracts/quality_gates.py`
  (`DomainQualityGateTemplateContract` / `templates_for_domain_profile(...)`)
  in the same slice, so `organ` does not inherit only `final_completion`
- declare any new stage, family, prompt, or diagnostics vocabulary in
  `contracts/guided_flow.py` / `contracts/router.py` before it reaches session
  state or public payloads; do not add free-form session keys
- keep any transport-visible organ guidance on the existing
  `reference_images(...)`, `router_get_status(...)`, and staged checkpoint
  surfaces instead of creating a parallel organ surface
- when the live refinement route or planner still reports `anatomy`, normalize
  that vocabulary explicitly into the public guided-state contract
  `domain_profile="organ"` on router/guided/checkpoint surfaces rather than
  letting both labels leak into the runtime
- route `fused`, `embedded`, `attached`, and `paired` semantics through the
  current `spatial_graph.py`, `contracts/scene.py`, and
  `quality_gate_verifier.py` substrate by mapping them onto explicit generic
  gate/truth shapes such as `attachment_seam`, `support_contact`,
  `opening_or_cut`, `shape_profile`, and `symmetry_pair` before adding
  domain-specific metadata or tool exposure
- if tool metadata needs organ-specific search/visibility cues, keep
  `_schema.json`, loader/alignment tests, and the `check-router-tool-metadata`
  hook in the same owner lane

## Pseudocode

```python
domain_profile = "organ"
guided_flow_state = seed_organ_flow(primary_mass_then_lobes_then_cavities)
relation_policy = map_organ_relations_to_gate_semantics()
verifier_inputs = derive_organ_relation_checks_from_spatial_graph(domain_profile, relation_policy)
visibility_rules = expose_bounded_organ_surface_for(guided_flow_state.current_step, domain_profile)
```

## Runtime / Security Contract Notes

- no default public path to unrestricted high-resolution sculpt
- organ relation hints remain advisory; verifier authority stays unchanged
- any new anatomy-facing helper must stay bounded and documented as
  visualization-oriented only

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_naming_policy.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`
- `tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py`
- `tests/unit/adapters/mcp/test_quality_gate_contracts.py`
- `tests/unit/adapters/mcp/test_quality_gate_intake.py`
- `tests/unit/adapters/mcp/test_quality_gate_verifier.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/unit/router/infrastructure/test_metadata_loader.py`
- `tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/scene/test_spatial_graph_service.py`
- `tests/unit/tools/modeling/test_modeling_tools.py`
- `tests/unit/tools/mesh/test_mesh_organic.py`
- `tests/unit/tools/sculpt/test_sculpt_tools.py`
- `tests/unit/tools/lattice/test_lattice_handler.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_mcp_transport_modes.py` as supplemental transport
  plumbing smoke, not as organ guided/reference parity proof
- `tests/e2e/router/test_guided_manual_handoff.py`
- `tests/e2e/vision/test_guided_organ_reconstruction.py`

## Docs To Update

- likely new `_docs/_PROMPTS/REFERENCE_GUIDED_ORGAN_BUILD.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the first organ guided-surface slice
  ships.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_guided_naming_policy.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_router_elicitation.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_prompt_catalog.py tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py tests/unit/adapters/mcp/test_quality_gate_contracts.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/router/application/test_router_contracts.py tests/unit/router/infrastructure/test_metadata_loader.py tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/scene/test_spatial_graph_service.py tests/unit/tools/modeling/test_modeling_tools.py tests/unit/tools/mesh/test_mesh_organic.py tests/unit/tools/sculpt/test_sculpt_tools.py tests/unit/tools/lattice/test_lattice_handler.py -q`
- `Outside sandbox before closeout: PYTHONPATH=. poetry run pytest ./tests/unit`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run check-router-tool-metadata --all-files`
- `Supplemental focused lane while iterating: poetry run pytest tests/e2e/router/test_guided_manual_handoff.py -q`
- `Supplemental focused lane while iterating: poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `Supplemental focused lane while iterating: poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py -q`
- `Supplemental focused lane while iterating: poetry run pytest tests/e2e/integration/test_mcp_transport_modes.py -q`
- `Supplemental future dedicated organ lane once the file exists: poetry run pytest tests/e2e/vision/test_guided_organ_reconstruction.py -q`
- `Outside sandbox before closeout: poetry run python scripts/run_e2e_tests.py`

## Status / Board Update

- keep `_docs/_TASKS/README.md` on the umbrella `TASK-137` row; this leaf stays
  nested under the parent umbrella
- if organ loop semantics land in more than one implementation wave, keep
  follow-on leaves explicit instead of broadening this file back into an
  oversized catch-all
