# TASK-128-01-01-02: Generic Creature Prompt Wording and Public Docs

**Parent:** [TASK-128-01-01](./TASK-128-01-01_Generic_Creature_Prompt_Catalog_Exposure.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Generalize the exposed creature prompt wording so it stays useful for squirrels,
foxes, birds, stylized quadrupeds, and similar staged creature builds without
requiring one prompt per species.

## Current Drift To Resolve

The current file still uses squirrel-heavy wording because it grew out of a
real eval prompt. Once the prompt becomes a first-class MCP asset, the docs
must present squirrel as an example, not as the product contract.

## Repository Touchpoints

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Acceptance Criteria

- the public prompt wording clearly describes a generic creature flow
- squirrel remains an example, not the defining product contract
- public docs point users toward the generic prompt asset name instead of a
  hidden markdown file or operator lore

## Docs To Update

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
