# TASK-138-02: Guided Character Flow, Appendage, And Garment Boundaries

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-138](./TASK-138_Anatomy_Aware_Reference_Guided_Biped_And_Fantasy_Character_Reconstruction.md)
**Depends On:** [TASK-138-01](./TASK-138-01_Humanoid_Contract_Symmetry_And_Fidelity_Tiers.md)
**Objective:** Turn the character contract into a usable body-first guided flow with bounded appendage and garment/armor boundaries, while keeping later armature work as an explicit handoff boundary and not as an implementation slice that changes the armature MCP contract itself.
**Repository Touchpoints:** `server/adapters/mcp/session_capabilities_state.py`, `server/adapters/mcp/session_capabilities_flow.py`, `server/adapters/mcp/session_capabilities_runtime_glue.py`, `server/adapters/mcp/transforms/visibility_policy.py`, `server/adapters/mcp/discovery/search_surface.py`, `server/adapters/mcp/areas/modeling.py`, `server/adapters/mcp/areas/mesh.py`, `server/adapters/mcp/areas/scene.py`, `server/router/infrastructure/tools_metadata/modeling/`, `server/router/infrastructure/tools_metadata/mesh/`, `server/router/infrastructure/tools_metadata/reference/`, `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`, `tests/unit/adapters/mcp/test_visibility_policy.py`, `tests/unit/adapters/mcp/test_search_surface.py`, `tests/unit/tools/mesh/test_mesh_symmetry_fill.py`, likely new `_docs/_PROMPTS/REFERENCE_GUIDED_CHARACTER_BUILD.md`, `_docs/_MCP_SERVER/README.md`
**Acceptance Criteria:** a biped/fantasy goal can reach a bounded body-first guided path; appendages and armor/garment seating are explicit later-stage boundaries; armature work remains a follow-on handoff recommendation and no armature MCP behavior/contracts are widened in this slice.

## Implementation Notes

- keep the first character flow body-first:
  - torso/pelvis
  - legs
  - arms
  - head/neck
  - hands/feet
  - optional appendages
  - optional garment/armor seating
- keep appendages and garments/armor explicit bounded follow-ons, not implicit
  core body work
- armature-related readiness may be reported later, but this slice should only
  shape visibility, sequencing, and handoff wording around that boundary; it
  should not change the public armature tool contracts themselves

## Pseudocode

```python
if domain_profile == "character":
    guided_flow_state = seed_character_flow(
        torso_then_legs_then_arms_then_head_then_hands_feet
    )
    appendage_policy = keep_appendages_and_gear_as_later_bounded_followons()
    visibility_rules = expose_body_first_tools(guided_flow_state.current_step)
```

## Runtime / Security Contract Notes

- do not widen the public surface into unrestricted character sculpting or full
  rigging
- body-part relation hints remain advisory; verifier authority stays unchanged
- any armature-adjacent follow-up must stay separate from the body-first
  reconstruction slice; this leaf may only shape the handoff boundary, not the
  armature runtime contract

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/tools/mesh/test_mesh_symmetry_fill.py`

## Docs To Update

- likely new `_docs/_PROMPTS/REFERENCE_GUIDED_CHARACTER_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the first character guided-surface slice
  ships.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/tools/mesh/test_mesh_symmetry_fill.py -q`
