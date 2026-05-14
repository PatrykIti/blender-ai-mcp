# TASK-168-01: Guided State Graph And Pre-Dispatch Action Shields

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-168](./TASK-168_Profile_Bound_Orchestrator_Shielding_Feedback_And_Memory_Containment.md)
**Objective:** Turn the current guided phase/role model into a hard runtime state graph plus one pre-dispatch shield that can block, rewrite, or route external controller actions before they mutate Blender in the wrong phase.
**Repository Touchpoints:** `server/adapters/mcp/session_capabilities_flow.py`, `server/adapters/mcp/session_capabilities_registry.py`, `server/adapters/mcp/session_capabilities_runtime_glue.py`, `server/adapters/mcp/router_helper.py`, `server/adapters/mcp/transforms/visibility_policy.py`, `server/adapters/mcp/guided_mode.py`, `server/router/application/router.py`, `tests/unit/adapters/mcp/test_context_bridge.py`, `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`, `tests/unit/router/application/test_supervisor_router.py`, `tests/e2e/router/test_guided_manual_handoff.py`, `tests/e2e/integration/test_guided_streamable_spatial_support.py`
**Acceptance Criteria:**
- the guided runtime exposes one explicit phase/state graph for profile-bound action eligibility
- mutating tool calls in forbidden states fail closed before dispatch with machine-readable block reasons
- corrected multi-step router calls are checked step-by-step against the same shield, not only by final result
- `checkpoint_iterate` can require compare/support actions before additional mutators
- manual guided squirrel flows no longer retrigger unrelated workflow heuristics during ordinary transforms

## Implementation Notes

- preserve the existing separation:
  - visibility shaping
  - guided state persistence
  - routed execution
  - Blender truth
- add one explicit pre-dispatch decision seam, for example:
  - `allow`
  - `deny`
  - `rewrite`
  - `require_verify`
- the shield must receive:
  - surface profile
  - current phase
  - guided current_step
  - spatial_refresh_required
  - allowed_families
  - allowed_roles
  - missing_roles
  - tool name
  - tool args
  - whether the step was router-corrected
- if `current_step == checkpoint_iterate`, default to fail closed on new
  modeling/mesh/macro mutators unless the same state explicitly exposes the
  required role/workset exception
- squirrel regression anchor:
  - `guided_role="eye_pair"` must not be treated as a valid guided role in the
    creature execution shield
  - manual no-match creature goals must preserve explicit goal context strongly
    enough to suppress unrelated heuristics like `tower_workflow`

## Pseudocode

```python
decision = evaluate_guided_action_policy(
    surface_profile=session.surface_profile,
    phase=session.phase,
    guided_flow_state=session.guided_flow_state,
    tool_name=tool_name,
    params=params,
    router_corrected=router_applied,
)

if decision.kind == "deny":
    return blocked_response(decision)
if decision.kind == "rewrite":
    params = decision.rewritten_params
if decision.kind == "require_verify":
    mark_next_step_must_verify(...)
dispatch(...)
```

## Runtime / Security Contract Notes

- fail closed on out-of-phase mutators
- do not trust caller-supplied family/role hints before validation
- shields must run on corrected router steps too
- tool visibility remains a support mechanism; it is not sufficient by itself as
  the only policy layer

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/router/application/test_supervisor_router.py`
- `tests/e2e/router/test_guided_manual_handoff.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Docs To Update

- `_docs/_ROUTER/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Changelog Impact

- historical closeout entry ownership belongs to
  [TASK-168-04](./TASK-168-04_Profile_Contract_Rewrite_Validation_And_Closeout.md)

## Status / Board Update

- remains nested under `TASK-168`
- should close before the feedback/manifest slices claim a stable runtime contract

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_context_bridge.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/router/application/test_supervisor_router.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/router/test_guided_manual_handoff.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_streamable_spatial_support.py -q`

## Validation Category

- focused unit and guided runtime integration tests
- `git diff --check`
