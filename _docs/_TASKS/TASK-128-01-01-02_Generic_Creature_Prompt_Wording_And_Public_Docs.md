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

There is also a runtime-surface wording drift to close:

- the prompt still teaches squirrel as the de facto product path instead of a
  generic creature contract
- the prompt still implies direct `scene_clean_scene(...)` usage in places
  where the real `llm-guided` bootstrap surface expects the sanctioned guided
  utility path (`search_tools(...)` -> `call_tool(...)`)

This leaf should not be treated as a substitute for real prompt exposure.
Its job is to align the wording/docs *after* the asset is genuinely visible on
the MCP surface, not to let docs-only wording masquerade as shipped prompt
support.

## Repository Touchpoints

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_MCP_SERVER/README.md`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Acceptance Criteria

- the public prompt wording clearly describes a generic creature flow
- squirrel remains an example, not the defining product contract
- the wording/docs teach the real `llm-guided` operating path:
  utility/bootstrap actions use the sanctioned discovery/proxy flow when the
  tool is not directly visible on bootstrap
- public docs point users toward the generic prompt asset name instead of a
  hidden markdown file or operator lore
- the wording/docs explicitly assume one real MCP prompt asset exists, so the
  parent subtask cannot be “completed” while runtime still returns
  `Unknown prompt` for that asset name
- docs regressions explicitly protect both:
  - generic creature positioning
  - runtime-surface-consistent utility/bootstrap instructions

## Docs To Update

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
