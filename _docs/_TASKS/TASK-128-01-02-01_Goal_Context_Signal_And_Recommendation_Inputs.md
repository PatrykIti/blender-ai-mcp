# TASK-128-01-02-01: Goal Context Signal and Recommendation Inputs

**Parent:** [TASK-128-01-02](./TASK-128-01-02_Goal_Aware_Creature_Prompt_Recommendations.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Define the bounded goal/session inputs that may influence
`recommended_prompts`, such as creature/animal/organic intent and low-poly
styling hints.

## Repository Touchpoints

- `server/adapters/mcp/prompts/prompt_catalog.py`
- `server/adapters/mcp/session_state.py`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- the recommendation inputs are explicit and bounded
- goal-aware logic does not depend on hidden ad hoc heuristics
- docs explain which session signals matter for creature prompt selection

## Docs To Update

- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- include in the parent slice changelog entry when shipped
