# TASK-128-01-01-01: Creature Prompt Catalog Entry and Tagging

**Parent:** [TASK-128-01-01](./TASK-128-01-01_Generic_Creature_Prompt_Catalog_Exposure.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Add one explicit prompt-catalog entry for `reference_guided_creature_build`
with generic creature-facing naming, description, and tags.

## Current Drift To Resolve

The runtime currently exposes `getting_started`, `guided_session_start`,
`workflow_router_first`, demo prompts, and `recommended_prompts`, but not the
existing creature build guide. This leaf closes that exact catalog/provider
gap.

The leaf also needs to pin down the real runtime failure cases:

- the prompt is absent from `list_prompts()`
- native `render_prompt("reference_guided_creature_build")` still fails as an
  unknown prompt
- the tool bridge therefore cannot recover it through `get_prompt(...)`

## Repository Touchpoints

- `server/adapters/mcp/prompts/prompt_catalog.py`
- `server/adapters/mcp/prompts/provider.py`
- `server/adapters/mcp/prompts/rendering.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_prompt_provider.py`
- `tests/unit/adapters/mcp/test_prompts_bridge.py`

## Acceptance Criteria

- the prompt catalog/provider exposes the new prompt asset with the stable name
  `reference_guided_creature_build`
- the new asset is reachable through the shaped prompt bridge as the same
  stable catalog entry
- the native prompt path and the tool-compatible bridge path are both covered by
  regressions, so the prompt cannot silently exist in only one delivery mode
- catalog metadata clearly marks it as guided creature/reference work
- tests verify it appears alongside the existing curated prompt set

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_prompt_provider.py`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_prompts_bridge.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
