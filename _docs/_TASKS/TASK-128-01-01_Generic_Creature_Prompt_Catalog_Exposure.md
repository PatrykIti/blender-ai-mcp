# TASK-128-01-01: Generic Creature Prompt Catalog Exposure

**Parent:** [TASK-128-01](./TASK-128-01_Guided_Creature_Prompting_Handoff_And_Discovery_Hints.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Promote the already-written
`_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md` file into the real MCP
prompt surface instead of leaving it as docs-only/operator-only guidance.

## Current Runtime Baseline

The prompt bridge and native prompt provider already work on `llm-guided`.
This subtask is specifically about catalog exposure of the existing creature
prompt asset, not about building a second prompt-delivery path.

## Scope

This subtask covers:

- adding one explicit prompt-catalog entry for generic creature work
- tagging and describing it so it is clearly reusable beyond squirrels
- aligning public prompt/docs wording with that generic positioning

## Acceptance Criteria

- `reference_guided_creature_build` is visible through the prompt provider and
  the `llm-guided` prompt bridge (`list_prompts` / `get_prompt`)
- the prompt description/tags position it as generic creature guidance, not a
  squirrel-only hardcoded path
- prompt docs and public tool summary mention the new exposed asset
- regression tests fail if the creature prompt silently falls back to
  docs-only visibility again

## Repository Touchpoints

- `server/adapters/mcp/prompts/prompt_catalog.py`
- `server/adapters/mcp/prompts/provider.py`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_prompt_provider.py`
- `tests/unit/adapters/mcp/test_prompts_bridge.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `_docs/_PROMPTS/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_prompt_provider.py`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_prompts_bridge.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-128-01-01-01](./TASK-128-01-01-01_Creature_Prompt_Catalog_Entry_And_Tagging.md) | Add the catalog/provider entry and stable generic tags |
| 2 | [TASK-128-01-01-02](./TASK-128-01-01-02_Generic_Creature_Prompt_Wording_And_Public_Docs.md) | Align wording/docs so the prompt is generic-creature, not squirrel-specific |
