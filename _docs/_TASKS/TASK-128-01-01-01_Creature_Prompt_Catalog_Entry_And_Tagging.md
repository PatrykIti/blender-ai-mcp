# TASK-128-01-01-01: Creature Prompt Catalog Entry and Tagging

**Parent:** [TASK-128-01-01](./TASK-128-01-01_Generic_Creature_Prompt_Catalog_Exposure.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Add one explicit prompt-catalog entry for `reference_guided_creature_build`
with generic creature-facing naming, description, and tags.

## Repository Touchpoints

- `server/adapters/mcp/prompts/prompt_catalog.py`
- `server/adapters/mcp/prompts/provider.py`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_prompt_provider.py`

## Acceptance Criteria

- the prompt catalog/provider exposes the new prompt asset
- catalog metadata clearly marks it as guided creature/reference work
- tests verify it appears alongside the existing curated prompt set

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_prompt_provider.py`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
