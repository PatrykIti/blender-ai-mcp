# TASK-155-02-05: Checkpoint Role Summary Consistency

**Parent:** [TASK-155-02](./TASK-155-02_Governor_Workset_Refresh_And_Bootstrap_Discipline.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Align `allowed_roles`, `missing_roles`, and execution policy after checkpoint
and spatial-refresh transitions so the model does not see `allowed_roles=[]`
while role-sensitive calls such as `tail_mass` are still accepted.

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/router.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`

## Acceptance Criteria

- role summaries describe the same role set that `_evaluate_guided_execution_policy(...)`
  will allow
- `checkpoint_iterate` and post-refresh states expose missing secondary or
  corrective roles when those roles are still legal
- if a role is not legal, execution blocks it consistently and returns the
  same role/family explanation as status does
- docs/prompts do not ask the model to infer role legality from `allowed_families`
  when role fields disagree

## Tests To Add/Update

- Unit:
  - add checkpoint/post-refresh role-summary cases to
    `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
  - add router-helper policy parity cases to
    `tests/unit/adapters/mcp/test_context_bridge.py`
  - update docs parity in `tests/unit/adapters/mcp/test_public_surface_docs.py`
- E2E:
  - extend `tests/e2e/integration/test_guided_surface_contract_parity.py`
    around checkpoint -> allowed role -> execution behavior

## Changelog Impact

- include in the TASK-155 changelog entry
