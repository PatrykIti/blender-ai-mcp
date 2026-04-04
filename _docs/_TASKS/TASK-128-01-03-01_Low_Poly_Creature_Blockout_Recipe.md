# TASK-128-01-03-01: Low-Poly Creature Blockout Recipe

**Parent:** [TASK-128-01-03](./TASK-128-01-03_Creature_Aware_Guided_Handoff_And_Tool_Recipes.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define the bounded low-poly creature starter recipe that should be favored for
generic reference-guided creature blockout work on `llm-guided`.

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- the low-poly recipe explicitly favors modeling/mesh blockout tools such as
  primitive creation, transform, selection, extrude, loop cut, bevel,
  symmetrize, merge-by-distance, and dissolve before broader macro or sculpt
  paths
- the first creature starter recipe keeps finishing/sculpt tools out of the
  initial direct build recommendation set
- the recipe is generic enough for common creature/animal blockouts
- docs describe the recipe as the first-choice guided creature handoff

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`

## Docs To Update

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- include in the parent slice changelog entry when shipped
