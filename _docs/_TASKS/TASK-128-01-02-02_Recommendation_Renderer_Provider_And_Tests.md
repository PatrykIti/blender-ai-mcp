# TASK-128-01-02-02: Recommendation Renderer, Provider, and Tests

**Parent:** [TASK-128-01-02](./TASK-128-01-02_Goal_Aware_Creature_Prompt_Recommendations.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Implement the goal-aware recommendation path through prompt rendering/provider
surfaces and lock it with focused regression tests.

## Repository Touchpoints

- `server/adapters/mcp/prompts/rendering.py`
- `server/adapters/mcp/prompts/provider.py`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_prompt_provider.py`

## Acceptance Criteria

- the rendered recommendation output can surface the creature prompt when the
  goal/session warrants it
- the path stays deterministic and catalog-driven
- regression tests cover both creature and non-creature recommendation cases

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_prompt_provider.py`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
