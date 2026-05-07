# TASK-138-02: Guided Character Flow, Appendage, And Garment Boundaries

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-138](./TASK-138_Anatomy_Aware_Reference_Guided_Biped_And_Fantasy_Character_Reconstruction.md)
**Depends On:** [TASK-138-01](./TASK-138-01_Humanoid_Contract_Symmetry_And_Fidelity_Tiers.md)
**Objective:** Turn the character contract into a usable body-first guided flow with bounded appendage and garment/armor boundaries, while keeping later armature work as an explicit handoff boundary and not as an implementation slice that changes the armature MCP contract itself.
**Repository Touchpoints:** `server/adapters/mcp/contracts/guided_flow.py`, `server/adapters/mcp/contracts/router.py`, `server/adapters/mcp/guided_mode.py`, `server/adapters/mcp/guided_naming_policy.py`, `server/adapters/mcp/router_helper.py`, `server/adapters/mcp/session_capabilities.py`, `server/adapters/mcp/session_capabilities_bootstrap.py`, `server/adapters/mcp/session_capabilities_registry.py`, `server/adapters/mcp/session_capabilities_state.py`, `server/adapters/mcp/session_capabilities_flow.py`, `server/adapters/mcp/session_capabilities_runtime_glue.py`, `server/adapters/mcp/prompts/prompt_catalog.py`, `server/adapters/mcp/prompts/provider.py`, `server/adapters/mcp/prompts/rendering.py`, `server/adapters/mcp/transforms/visibility_policy.py`, `server/adapters/mcp/discovery/search_documents.py`, `server/adapters/mcp/discovery/search_surface.py`, `server/router/infrastructure/tools_metadata/modeling/modeling_create_primitive.json`, `server/router/infrastructure/tools_metadata/modeling/modeling_transform_object.json`, `server/router/infrastructure/tools_metadata/mesh/mesh_select.json`, `server/router/infrastructure/tools_metadata/mesh/mesh_select_targeted.json`, `server/router/infrastructure/tools_metadata/mesh/mesh_extrude_region.json`, `server/router/infrastructure/tools_metadata/mesh/mesh_loop_cut.json`, `server/router/infrastructure/tools_metadata/mesh/mesh_bevel.json`, `server/router/infrastructure/tools_metadata/mesh/mesh_symmetrize.json`, `server/router/infrastructure/tools_metadata/scene/macro_attach_part_to_surface.json`, `server/router/infrastructure/tools_metadata/scene/macro_align_part_with_contact.json`, `server/router/infrastructure/tools_metadata/scene/macro_cleanup_part_intersections.json`, `server/router/infrastructure/tools_metadata/scene/macro_place_symmetry_pair.json`, `server/router/infrastructure/tools_metadata/scene/macro_place_supported_pair.json`, `server/router/infrastructure/tools_metadata/scene/macro_adjust_relative_proportion.json`, `server/router/infrastructure/tools_metadata/scene/macro_adjust_segment_chain_arc.json`, `server/router/infrastructure/tools_metadata/reference/reference_images.json`, `server/router/infrastructure/tools_metadata/reference/reference_compare_stage_checkpoint.json`, `server/router/infrastructure/tools_metadata/reference/reference_iterate_stage_checkpoint.json`, `tests/unit/adapters/mcp/test_guided_mode.py`, `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`, `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`, `tests/unit/adapters/mcp/test_guided_naming_policy.py`, `tests/unit/adapters/mcp/test_prompt_catalog.py`, `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`, `tests/unit/adapters/mcp/test_prompt_provider.py`, `tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py`, `tests/unit/adapters/mcp/test_prompts_bridge.py`, `tests/unit/adapters/mcp/test_visibility_policy.py`, `tests/unit/adapters/mcp/test_search_surface.py`, `tests/unit/adapters/mcp/test_router_elicitation.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_session_phase.py`, `tests/unit/router/application/test_router_contracts.py`, `tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py`, `tests/e2e/router/test_guided_manual_handoff.py`, `tests/e2e/integration/test_guided_streamable_spatial_support.py`, likely new `_docs/_PROMPTS/REFERENCE_GUIDED_CHARACTER_BUILD.md`, `_docs/_PROMPTS/README.md`, `_docs/_MCP_SERVER/README.md`
**Acceptance Criteria:** router-guided character sessions initialize a stable `guided_handoff.recipe_id` / `guided_flow_state.flow_id` pair with `domain_profile="character"`; required prompts, search, and visibility expose a bounded body-first tool window plus explicit later appendage/garment follow-ons; armature guidance stays handoff-only and no armature MCP contract or test surface is widened in this slice.

## Implementation Notes

- keep the first character flow body-first:
  - torso/pelvis
  - legs
  - arms
  - head/neck
  - hands/feet
  - optional appendages
  - optional garment/armor seating
- use one stable contract naming pair for the new surface, for example
  `guided_handoff.recipe_id="low_poly_character_blockout"` and
  `guided_flow_state.flow_id="guided_character_flow"`, so prompt bundles,
  search, and visibility do not guess across several aliases
- replace the current character-like creature fallback only when the explicit
  character handoff is active; do not regress the existing creature surface for
  real animal goals
- keep appendages and garments/armor explicit bounded follow-ons, not implicit
  core body work
- armature-related readiness may be reported later, but this slice should only
  shape visibility, sequencing, and handoff wording around that boundary; it
  should not change the public armature tool contracts themselves

## Pseudocode

```python
if guided_handoff.recipe_id == "low_poly_character_blockout":
    guided_flow_state = seed_character_flow(
        flow_id="guided_character_flow",
        domain_profile="character",
        torso_then_legs_then_arms_then_head_then_hands_feet,
    )
    required_prompts = ["guided_session_start", "reference_guided_character_build"]
    appendage_policy = keep_appendages_and_gear_as_later_bounded_followons()
    visibility_rules = expose_body_first_tools(guided_flow_state.current_step)
```

## Runtime / Security Contract Notes

- do not widen the public surface into unrestricted character sculpting or full
  rigging
- body-part relation hints remain advisory; verifier authority stays unchanged
- any rig-handoff wording for this slice must live on router/guided/prompt
  surfaces, not in `server/adapters/mcp/areas/armature.py`
- any armature-adjacent follow-up must stay separate from the body-first
  reconstruction slice; this leaf may only shape the handoff boundary, not the
  armature runtime contract

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_naming_policy.py`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`
- `tests/unit/adapters/mcp/test_prompt_provider.py`
- `tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py`
- `tests/unit/adapters/mcp/test_prompts_bridge.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py`
- `tests/e2e/router/test_guided_manual_handoff.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Docs To Update

- likely new `_docs/_PROMPTS/REFERENCE_GUIDED_CHARACTER_BUILD.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the first character guided-surface slice
  ships.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_guided_naming_policy.py tests/unit/adapters/mcp/test_prompt_catalog.py tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py tests/unit/adapters/mcp/test_prompt_provider.py tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py tests/unit/adapters/mcp/test_prompts_bridge.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_router_elicitation.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_session_phase.py tests/unit/router/application/test_router_contracts.py -q`
- `poetry run pytest ./tests/unit`
- `PYTHONPATH=. poetry run pytest tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py -q`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run check-router-tool-metadata --all-files`
- `poetry run python scripts/run_e2e_tests.py`

## Status / Board Update

- keep `TASK-138-03` open after this leaf lands; `TASK-138-02` establishes the
  body-first guided surface but does not close regression/docs closeout
- if later work needs real armature runtime changes, promote that as a separate
  `Follow-on After: TASK-138` task rather than reopening this leaf
