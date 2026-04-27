# TASK-128-01-02-02: Recommendation Renderer, Provider, and Tests

**Parent:** [TASK-128-01-02](./TASK-128-01-02_Goal_Aware_Creature_Prompt_Recommendations.md)
**Status:** ✅ Done
**Priority:** 🟠 High

## Objective

Implement the goal-aware recommendation path through prompt rendering/provider
surfaces and lock it with focused regression tests.

## Current Drift To Resolve

The current provider reads phase/profile from session state but not the active
goal/domain context. This leaf is the wiring step that turns the bounded input
definition into actual rendered recommendations.

The leaf should explicitly close three aligned failures:

- `render_recommended_prompts(...)` still behaves as phase/profile-only
- provider resolution still stops at phase/profile even when session goal is
  available
- prompt-bridge regressions do not yet prove that creature and non-creature
  sessions diverge correctly under the same phase/profile

## Repository Touchpoints

- `server/adapters/mcp/prompts/prompt_catalog.py`
- `server/adapters/mcp/prompts/rendering.py`
- `server/adapters/mcp/prompts/provider.py`
- `server/adapters/mcp/session_capabilities.py`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_prompt_provider.py`
- `tests/unit/adapters/mcp/test_prompts_bridge.py`

## Acceptance Criteria

- the rendered recommendation output can surface the creature prompt when the
  goal/session warrants it
- the path stays deterministic and catalog-driven
- regression coverage proves that two sessions with the same phase/profile but
  different goal context can yield different recommendation results
- regression tests cover both creature and non-creature recommendation cases
- tool-compatible prompt bridge coverage stays aligned with the native prompt
  provider so `recommended_prompts` does not diverge across client types

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_prompt_provider.py`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_prompts_bridge.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
