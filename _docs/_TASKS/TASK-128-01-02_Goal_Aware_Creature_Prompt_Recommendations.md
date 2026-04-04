# TASK-128-01-02: Goal-Aware Creature Prompt Recommendations

**Parent:** [TASK-128-01](./TASK-128-01_Guided_Creature_Prompting_Handoff_And_Discovery_Hints.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Extend prompt recommendation so creature-oriented sessions can surface the
generic creature-build prompt based on goal/domain signals, not only on phase
and surface profile.

## Business Problem

`recommended_prompts` currently knows about:

- session phase
- surface profile

It does not know enough about:

- current goal wording
- creature/organic domain hints
- low-poly vs broader organic blockout intent

That keeps the best creature prompt discoverable only through external docs or
manual operator knowledge.

## Current Runtime Baseline

`recommended_prompts` is already a real MCP/native prompt surface, but its
logic is still deterministic only by:

- session phase
- surface profile

This slice extends that deterministic path with bounded goal/session context
instead of replacing it with fuzzy heuristics.

## Repository Touchpoints

- `server/adapters/mcp/prompts/prompt_catalog.py`
- `server/adapters/mcp/prompts/rendering.py`
- `server/adapters/mcp/prompts/provider.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/session_state.py`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_prompt_provider.py`
- `tests/unit/adapters/mcp/test_prompts_bridge.py`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- recommendation rules can use bounded creature-oriented goal/session context
- the recommendation path stays deterministic and catalog-driven
- docs explain why creature prompts can now be suggested during guided
  creature sessions
- tests cover both creature and non-creature guided sessions so Slice A does
  not regress back to phase/profile-only behavior

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_prompt_provider.py`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_prompts_bridge.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-128-01-02-01](./TASK-128-01-02-01_Goal_Context_Signal_And_Recommendation_Inputs.md) | Define which goal/session signals can drive creature prompt recommendations |
| 2 | [TASK-128-01-02-02](./TASK-128-01-02-02_Recommendation_Renderer_Provider_And_Tests.md) | Wire the recommendation flow through rendering/provider/tests without losing determinism |
