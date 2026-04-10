# TASK-130-01-02: Explicit First Step Request Triage And Recovery Path

**Parent:** [TASK-130-01](./TASK-130-01_Default_Guided_Bootstrap_And_Request_Triage_Consistency.md)
**Depends On:** [TASK-130-01-01](./TASK-130-01-01_Align_Runtime_Default_Client_Examples_And_Operator_Story.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Make the first-step request classification and early recovery path explicit so
the model does not oscillate between goal setup, utility prep, and search-only
drift.

## Repository Touchpoints

- `server/adapters/mcp/surfaces.py`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/README.md`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Planned Validation Matrix

- build/workflow goal starts from `router_get_status()` -> `router_set_goal(...)`
- utility/capture request skips goal-setting and uses the guided utility path
- manual-build continuation treats `guided_handoff` / `guided_flow_state` as
  the active contract, not optional prose

## Acceptance Criteria

- the first-step triage/recovery rules are explicit and consistent in docs

## Changelog Impact

- include in the parent TASK-130 changelog entry
