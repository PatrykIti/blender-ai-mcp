# TASK-150-02-02: Creature And Building Domain Overlay Policies

**Parent:** [TASK-150-02](./TASK-150-02_Domain_Profile_Selection_And_Overlay_Policy.md)
**Depends On:** [TASK-150-02-01](./TASK-150-02-01_Generic_Flow_Skeleton_And_Step_Vocabulary.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define the first concrete domain overlays for `creature` and `building`, while
keeping `generic` as the fallback profile.

## Repository Touchpoints

- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/prompts/prompt_catalog.py`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Planned File Work

- Modify:
  - `server/adapters/mcp/areas/router.py`
  - `server/adapters/mcp/session_capabilities.py`
  - `server/adapters/mcp/prompts/prompt_catalog.py`
  - `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- Create later if needed:
  - building-specific prompt asset or profile doc

## Detailed Implementation Notes

- creature overlay should not just mean "squirrel mode"; it should express the
  common structural needs of multi-part creature reconstruction
- building overlay should bias toward:
  - spatial framing
  - structural anchor/scope
  - coarse massing / facade / opening sequencing
- the overlay should modify:
  - initial step
  - required checks
  - blocked families
  - required prompts
  but should not fork the entire runtime into separate bespoke state machines

## Planned Test Files And Scenarios

- Modify `tests/unit/adapters/mcp/test_router_elicitation.py`
  - creature goal -> `domain_profile == "creature"`
  - building goal -> `domain_profile == "building"`
  - neutral goal -> `domain_profile == "generic"`
- Create `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
  - keyword/recipe-driven profile selection
  - overlay-specific required checks/prompts
  - regression against accidental collapse of all goals into `creature`

## Example Test Sketch

```python
def test_building_goal_selects_building_overlay():
    state = initialize_guided_flow_state(
        goal="rebuild a low-poly watchtower from front and side references",
        guided_handoff={...},
    )
    assert state.domain_profile == "building"
    assert "scene_view_diagnostics" in state.required_checks
```

## Acceptance Criteria

- deterministic selection can choose `creature` or `building`
- overlays can alter step ordering, required checks, and required prompts
- `generic` remains the fallback instead of collapsing unknown goals into one
  of the specialized profiles

## Pseudocode Sketch

```python
if goal_matches_creature(...) or guided_handoff.recipe_id == "low_poly_creature_blockout":
    domain_profile = "creature"
elif goal_matches_building(...):
    domain_profile = "building"
else:
    domain_profile = "generic"

DOMAIN_OVERLAYS = {
    "creature": {
        "required_prompts": ("reference_guided_creature_build",),
        "required_checks": ("scene_scope_graph", "scene_relation_graph", "scene_view_diagnostics"),
    },
    "building": {
        "required_checks": ("scene_scope_graph", "scene_view_diagnostics"),
    },
}
```

## Docs To Update

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `README.md`

## Tests To Add/Update

- router/domain-profile selection tests under `tests/unit/adapters/mcp/`

## Changelog Impact

- include in the parent TASK-150 changelog entry when shipped
