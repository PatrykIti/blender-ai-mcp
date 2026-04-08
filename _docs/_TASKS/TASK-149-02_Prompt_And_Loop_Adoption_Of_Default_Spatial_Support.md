# TASK-149-02: Prompt And Loop Adoption Of Default Spatial Support

**Parent:** [TASK-149](./TASK-149_Guided_Default_Spatial_Graph_And_View_Diagnostics_For_All_Goal_Oriented_Sessions.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Align guided prompts and loop guidance with the new rule that active
goal-oriented sessions always have direct spatial support tools available.

## Repository Touchpoints

- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `README.md`

## Acceptance Criteria

- prompt assets stop framing the spatial graph/view helpers as rare optional
  extras once a goal is active
- guided creature/build prompts explicitly tell the model to use those tools
  early for 3D orientation, not only after confusion appears
- loop guidance keeps truth/measure/assert authoritative while still promoting
  graph/view helpers as the default orientation layer

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `README.md`

## Tests To Add/Update

- docs parity coverage as needed in `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Changelog Impact

- include in the parent umbrella changelog entry when shipped
