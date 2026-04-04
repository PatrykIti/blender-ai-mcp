# TASK-128-01-01: Generic Creature Prompt Catalog Exposure

**Parent:** [TASK-128-01](./TASK-128-01_Guided_Creature_Prompting_Handoff_And_Discovery_Hints.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Promote `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md` into the MCP prompt
catalog as one generic creature-build asset instead of leaving it as
docs-only/operator-only guidance.

## Scope

This subtask covers:

- adding one explicit prompt-catalog entry for generic creature work
- tagging and describing it so it is clearly reusable beyond squirrels
- aligning public prompt/docs wording with that generic positioning

## Acceptance Criteria

- `reference_guided_creature_build` is visible through the prompt provider
- the prompt description/tags position it as generic creature guidance, not a
  squirrel-only hardcoded path
- prompt docs and public tool summary mention the new exposed asset

## Repository Touchpoints

- `server/adapters/mcp/prompts/prompt_catalog.py`
- `server/adapters/mcp/prompts/provider.py`
- `tests/unit/adapters/mcp/test_prompt_provider.py`
- `_docs/_PROMPTS/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_prompt_provider.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-128-01-01-01](./TASK-128-01-01-01_Creature_Prompt_Catalog_Entry_And_Tagging.md) | Add the catalog/provider entry and stable generic tags |
| 2 | [TASK-128-01-01-02](./TASK-128-01-01-02_Generic_Creature_Prompt_Wording_And_Public_Docs.md) | Align wording/docs so the prompt is generic-creature, not squirrel-specific |
