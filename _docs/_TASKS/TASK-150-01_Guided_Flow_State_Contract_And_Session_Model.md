# TASK-150-01: Guided Flow State Contract And Session Model

**Parent:** [TASK-150](./TASK-150_Server_Driven_Guided_Flow_State_Step_Gating_And_Domain_Profiles.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define one generic machine-readable `guided_flow_state` contract and persist it
 in MCP session state for `llm-guided`.

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/contracts/router.py`
- `server/adapters/mcp/areas/router.py`

## Acceptance Criteria

- `guided_flow_state` has a typed envelope with at least:
  - `flow_id`
  - `domain_profile`
  - `current_step`
  - `completed_steps`
  - `required_checks`
  - `required_prompts`
  - `next_action` or `next_actions`
- the state persists across normal same-session guided calls
- `router_set_goal(...)` and `router_get_status(...)` can expose the state

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_session_phase.py`

## Changelog Impact

- include in the parent umbrella changelog entry when shipped

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-150-01-01](./TASK-150-01-01_Flow_State_Types_Contracts_And_Session_Keys.md) | Define the typed flow-state envelope, contract models, and session-storage keys |
| 2 | [TASK-150-01-02](./TASK-150-01-02_Router_Status_Exposure_And_State_Transition_Baseline.md) | Expose flow state through router/status payloads and define baseline transition semantics |
