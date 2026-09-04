# TASK-128-01-02-01: Goal Context Signal and Recommendation Inputs

**Parent:** [TASK-128-01-02](./TASK-128-01-02_Goal_Aware_Creature_Prompt_Recommendations.md)
**Status:** ✅ Done
**Priority:** 🟠 High

## Objective

Define the bounded goal/session inputs that may influence
`recommended_prompts`, such as creature/animal/organic intent and low-poly
styling hints.

## Current Drift To Resolve

This leaf should define the exact allowed context for prompt recommendation.
Without that, the runtime will keep falling back to phase/profile-only logic or
grow ad hoc heuristics that are hard to test.

The key technical ambiguity to close is that the repo already stores the active
goal in session state, but the task does not yet say explicitly which parts of
that session state may drive `recommended_prompts` and which parts must stay
out of scope.

## Repository Touchpoints

- `server/adapters/mcp/prompts/prompt_catalog.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/session_state.py`
- `tests/unit/adapters/mcp/test_session_phase.py`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- the recommendation inputs are explicit and bounded
- goal-aware logic does not depend on hidden ad hoc heuristics
- the allowed inputs are limited to current session/runtime state such as
  active goal wording, phase/profile, and other explicit guided-session fields;
  vision output and free-form search history are not recommendation inputs
- the task explicitly distinguishes:
  - session fields that may influence recommendation ranking
  - session fields that may be persisted for other purposes but must not become
    recommendation inputs by default
- docs explain which session signals matter for creature prompt selection

## Docs To Update

- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_session_phase.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
