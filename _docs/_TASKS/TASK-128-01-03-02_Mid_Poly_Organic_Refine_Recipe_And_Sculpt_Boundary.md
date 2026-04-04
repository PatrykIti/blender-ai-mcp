# TASK-128-01-03-02: Mid-Poly Organic Refine Recipe and Sculpt Boundary

**Parent:** [TASK-128-01-03](./TASK-128-01-03_Creature_Aware_Guided_Handoff_And_Tool_Recipes.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Define the next bounded recipe for mid-poly organic refinement and document
when sculpt may be suggested later without becoming the default creature
starting path.

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Acceptance Criteria

- the repo distinguishes low-poly blockout from mid-poly organic refinement
- sculpt stays explicitly gated behind later refinement/handoff logic and does
  not become a directly visible default creature build tool
- docs describe the sculpt boundary in product terms

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Changelog Impact

- include in the parent slice changelog entry when shipped
