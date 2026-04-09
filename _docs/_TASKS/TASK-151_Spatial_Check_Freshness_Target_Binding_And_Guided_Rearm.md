# TASK-151: Spatial Check Freshness, Target Binding, And Guided Re-Arm

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Guided Runtime / Spatial Discipline
**Estimated Effort:** Large
**Follow-on After:** [TASK-150](./TASK-150_Server_Driven_Guided_Flow_State_Step_Gating_And_Domain_Profiles.md)

## Objective

Close the main guided-runtime gap left after TASK-150: spatial checks are
still too easy to satisfy once, then forget.

The follow-on goal is to make the guided server treat spatial facts as:

- target-bound
- freshness-bound
- re-armable after material scene changes

so the model cannot satisfy `scene_view_diagnostics(...)` on an unrelated
object and then free-run for the next hundred tool calls without refreshing the
spatial layer.

## Current Code Baseline

The current guided runtime already has the right first-pass skeleton, but the
remaining gap is visible directly in code:

- `server/adapters/mcp/areas/scene.py`
  - `scene_scope_graph(...)`, `scene_relation_graph(...)`, and
    `scene_view_diagnostics(...)` call
    `record_guided_flow_spatial_check_completion(ctx, tool_name=...)` after a
    successful payload
- `server/adapters/mcp/session_capabilities.py`
  - `_mark_guided_flow_check_completed_dict(...)` marks checks completed by
    `tool_name` only
  - there is no active target-scope fingerprint and no spatial freshness
    bookkeeping
- `server/adapters/mcp/router_helper.py`
  - routed execution already knows the final effective tool/family/role, so it
    is the natural place to mark the spatial layer stale after successful
    scene-changing operations
- `server/adapters/mcp/transforms/visibility_policy.py`
  - build visibility still keys primarily off `guided_flow_state.current_step`,
    so a freshness-aware re-arm path needs one explicit machine-readable signal
    instead of prompt prose alone

This means TASK-151 is not a speculative cleanup. It is the next concrete
server/runtime step after the TASK-150 flow and execution-enforcement waves.

## Business Problem

TASK-150 delivered:

- machine-readable `guided_flow_state`
- domain overlays
- shared build families
- part-role registration
- family/role fail-closed execution policy
- role-group-driven step transitions

But real sessions still show two failures:

1. **Scope spoofing**
   one required spatial check can be satisfied on an unrelated object
   (for example `Camera`) instead of on the active guided target scope.

2. **Spatial staleness**
   after a scene reset, primitive creation, large transforms, or macro repairs,
   the old scope/relation/view facts may already be stale, but the runtime does
   not re-arm the required spatial checks.

This means the server still owns the *first* spatial gate, but not yet the
ongoing spatial discipline of the session.

## Acceptance Criteria

- required spatial checks are bound to the active guided target scope instead
  of being satisfiable on arbitrary unrelated objects
- material scene changes can mark the spatial layer stale
- the guided flow can re-arm required spatial checks after those changes
- later guided steps can explicitly require a spatial refresh before
  continuing when the last spatial state is stale
- transport-backed regression coverage proves the model does not need to guess
  whether spatial checks are still valid

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/areas/modeling.py`
- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/contracts/guided_flow.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TASKS/README.md`

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when this follow-on ships

## Detailed Implementation Notes

- target binding should live in one explicit flow/session contract field, not
  only in ad-hoc per-tool conditionals
- freshness invalidation should prefer one shared post-execution helper on the
  routed MCP path instead of duplicating stale-marking logic across every
  `scene_*` / `modeling_*` wrapper
- re-arm should remain machine-readable:
  - explicit freshness flags / versions on `guided_flow_state`
  - explicit `required_checks`
  - explicit `next_actions`
  - explicit visibility/execution narrowing while spatial refresh is pending
- public docs should explain the operator-visible semantics only after the
  runtime contract is real; the code leaves should not try to solve the issue
  with prompt wording alone

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-151-01](./TASK-151-01_Target_Bound_Spatial_Check_Validity.md) | Make required spatial checks prove facts about the active guided target scope instead of arbitrary objects |
| 2 | [TASK-151-02](./TASK-151-02_Spatial_Freshness_And_Rearm_Policy.md) | Track when spatial facts become stale and re-arm the required spatial layer after material scene changes |
| 3 | [TASK-151-03](./TASK-151-03_Regression_And_Docs_For_Spatial_Rearm.md) | Lock in the spatial re-arm model with transport coverage and operator docs |

## Status / Board Update

- promoted as a board-level follow-on because TASK-150 solved the first guided
  execution contract, but real sessions still need stronger target-bound and
  freshness-aware spatial discipline
