# TASK-145-03-02: Planner-First Prompting and Documentation

**Parent:** [TASK-145-03](./TASK-145-03_Guided_Adoption_Visibility_Docs_And_Regression_Pack.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High  
**Depends On:** [TASK-145-03-01](./TASK-145-03-01_Planner_And_Sculpt_Delivery_On_LLM_Guided.md)

## Objective

Update the guided documentation layer so the operator learns a consistent
planner-first read order:

- planner summary / family decision first
- sculpt blockers and handoff context next
- lower-level correction hints and raw vision prose after that

## Repository Touchpoints

- `server/adapters/mcp/prompts/prompt_catalog.py`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Acceptance Criteria

- prompt/docs ordering consistently tells the model to inspect planner outputs
  before dropping into free-form edits
- guided docs explain that sculpt remains bounded and preconditioned rather
  than a default fallback
- documentation stays aligned with the actual shaped public surface and does
  not instruct hidden or non-default tools

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Changelog Impact

- include in the parent TASK-145 changelog entry when shipped

## Status / Board Update

- no board change in this planning-only branch
