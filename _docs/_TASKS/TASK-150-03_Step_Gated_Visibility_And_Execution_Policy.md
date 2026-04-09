# TASK-150-03: Step-Gated Visibility And Execution Policy

**Parent:** [TASK-150](./TASK-150_Server_Driven_Guided_Flow_State_Step_Gating_And_Domain_Profiles.md)
**Depends On:** [TASK-150-01](./TASK-150-01_Guided_Flow_State_Contract_And_Session_Model.md), [TASK-150-02](./TASK-150-02_Domain_Profile_Selection_And_Overlay_Policy.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Make `llm-guided` visibility and execution behavior depend on guided flow step,
 not only coarse phase.

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/guided_mode.py`
- `server/adapters/mcp/discovery/search_surface.py`

## Acceptance Criteria

- step gating can narrow or widen tool visibility inside the same phase
- server behavior can require key checks or checkpoint actions before later
  tool families become available
- guided execution policy can distinguish broad build families such as
  primary masses, secondary parts, attachment/alignment, iterate, inspect,
  and finish instead of collapsing all post-bootstrap build work into one
  undifferentiated allow state
- the behavior remains explainable through typed server payloads instead of
  silent hidden-state changes

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/integration/`

## Changelog Impact

- include in the parent umbrella changelog entry when shipped

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-150-03-01](./TASK-150-03-01_Flow_Aware_Visibility_Rules_And_Search_Surface_Gating.md) | Make visibility and search/call behavior consult flow step and domain profile |
| 2 | [TASK-150-03-02](./TASK-150-03-02_Step_Completion_Checks_And_Execution_Blocks.md) | Define how required checks and blocked families prevent premature step progression |
| 3 | [TASK-150-03-03](./TASK-150-03-03_Generic_Families_Part_Roles_And_Execution_Enforcement.md) | Extend step gating into real execution enforcement using shared tool families, session-scoped part roles, and router/firewall policy |

## Completion Summary

- `llm-guided` step gating now covers:
  - visibility/list/search/call shaping
  - required checks
  - execution-time family/role enforcement
  - role-group-driven step transitions
