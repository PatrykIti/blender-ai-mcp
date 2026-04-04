# TASK-128-01: Guided Creature Prompting, Handoff, and Discovery Hints

**Parent:** [TASK-128](./TASK-128_Reference_Guided_Creature_Build_Surface_And_Perception_Reliability.md)
**Status:** 🚧 In Progress
**Priority:** 🔴 High

## Objective

Ship the first high-ROI creature-reliability slice by closing the audited gap
between the existing `llm-guided` platform baseline and the intended generic
creature operating surface.

## Business Problem

The repo already contains a useful creature-build prompt and a strong guided
reference loop, but the operational surface is still fragmented:

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md` exists but is not exposed
  by the prompt catalog
- `recommended_prompts` reacts only to phase/profile, not to
  creature-oriented goal context
- `guided_manual_build` remains too broad for creature blockout and still
  overexposes a macro-heavy shape
- tool metadata/search phrases under-rank the atomic modeling tools needed for
  ears, snout, tail, paws, silhouette, and proportion work

This slice is meant to fix the operating surface before adding another
perception module.

## Current Runtime Baseline

The repo already has the platform pieces that this slice should build on:

- prompt bridge tools and native prompt exposure
- search-first discovery on `llm-guided`
- typed `guided_manual_build` handoff on no-match
- staged reference compare / iterate with truth-first loop escalation

The problem is not missing platform scaffolding. The problem is that the
creature-specific shaping on top of that scaffolding is still incomplete.

## Current Drift To Resolve

Current audited drift is:

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md` is indexed in docs but is
  still not exposed by the prompt catalog/provider/bridge
- `recommended_prompts` still ignores active goal/domain context
- `guided_manual_build` still points to a broad macro-first recipe and build
  phase visibility expands into a large generic surface
- search metadata does not yet bias the model toward creature blockout tools
  for natural creature-focused phrases

## Business Outcome

If this slice is done correctly:

- generic creature guidance is directly discoverable through MCP prompt assets
- `llm-guided` handoff becomes creature-aware instead of forcing broad
  rediscovery
- search/discovery nudges the model toward the right blockout tools earlier
- the repo stops teaching squirrel-specific operator folklore as the main path

## Scope

This slice covers:

- prompt-catalog exposure for a generic creature-build prompt
- goal-aware prompt recommendation rules for creature-oriented guided sessions
- creature-aware handoff/tool recipe shaping for `guided_manual_build`
- metadata/search-hint enrichment for creature blockout tools
- prompt/docs/regression alignment for the refined guided surface

This slice does **not** cover:

- rebuilding the existing prompt bridge or search-first FastMCP platform layer
- redefining `guided_reference_readiness` or the staged reference loop baseline
- deterministic silhouette-analysis implementation
- new vision-model runtime integration
- sculpt-first creature workflows as the default path

## Acceptance Criteria

- a generic creature-build prompt is exposed through `list_prompts` /
  `get_prompt`, with native prompt exposure staying aligned to the same asset
- recommended prompt selection can favor the creature-build prompt when the
  session goal is creature-oriented
- the guided creature handoff exposes a smaller, more relevant build recipe for
  low-poly creature blockout
- tool discovery/search gains explicit creature-oriented metadata and prompt
  phrases
- docs and focused regression coverage describe the new guided creature path
- the task package no longer treats docs-only prompt files, broad macro-first
  handoffs, or generic search coverage as if they already satisfy Slice A

## Repository Touchpoints

- `server/adapters/mcp/prompts/prompt_catalog.py`
- `server/adapters/mcp/prompts/provider.py`
- `server/adapters/mcp/prompts/rendering.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/discovery/search_documents.py`
- `server/router/infrastructure/tools_metadata/modeling/`
- `server/router/infrastructure/tools_metadata/mesh/`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_prompt_provider.py`
- `tests/unit/adapters/mcp/test_prompts_bridge.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/unit/router/application/test_router_handler_parameters.py`
- `tests/e2e/router/test_guided_manual_handoff.py`
- `_docs/_PROMPTS/`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_prompt_provider.py`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_prompts_bridge.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/unit/router/application/test_router_handler_parameters.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/router/test_guided_manual_handoff.py`

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when this slice is completed

## Status / Board Update

- keep this slice promoted on `_docs/_TASKS/README.md` until the prompt,
  handoff, and search surfaces are aligned
- treat this as the active execution slice under [TASK-128](./TASK-128_Reference_Guided_Creature_Build_Surface_And_Perception_Reliability.md)

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-128-01-01](./TASK-128-01-01_Generic_Creature_Prompt_Catalog_Exposure.md) | Expose one generic creature-build prompt as a real MCP prompt asset |
| 2 | [TASK-128-01-02](./TASK-128-01-02_Goal_Aware_Creature_Prompt_Recommendations.md) | Make recommendations react to creature-oriented goal context, not only phase/profile |
| 3 | [TASK-128-01-03](./TASK-128-01-03_Creature_Aware_Guided_Handoff_And_Tool_Recipes.md) | Narrow `guided_manual_build` into explicit creature blockout recipe sets |
| 4 | [TASK-128-01-04](./TASK-128-01-04_Creature_Blockout_Metadata_Search_Hints_And_Regression_Pack.md) | Bias discovery/search/docs toward creature blockout language and regression coverage |
