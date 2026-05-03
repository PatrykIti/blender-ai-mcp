# TASK-159-04-02: Session Goal Bootstrap, Prompt Bundles, And Reference Readiness

**Parent:** [TASK-159-04](./TASK-159-04_Session_Capabilities_Modularization_And_Guided_State_Boundaries.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Extract goal bootstrap, domain-profile selection, prompt-bundle shaping,
reference-readiness helpers, and the goal-reset / partial-answer-merge seams
from `session_capabilities.py` without drifting router-start or
prompt-provider semantics.

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- likely new helper module such as `server/adapters/mcp/session_capabilities_bootstrap.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/prompts/provider.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`
- `tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py`
- `tests/e2e/router/test_guided_manual_handoff.py`

## Current Code Anchors

- `infer_phase_from_router_status(...)`
- `_select_guided_flow_domain_profile(...)`
- `clear_session_goal_state(...)`
- `clear_session_goal_state_async(...)`
- `merge_resolved_params_with_session_answers(...)`
- `merge_resolved_params_with_session_answers_async(...)`
- `_build_required_prompt_bundle(...)`
- `update_session_from_router_goal(...)`
- `build_guided_reference_readiness(...)`
- `build_guided_reference_readiness_payload(...)`

## Planned Code Shape

```python
from .session_capabilities_bootstrap import (
    clear_session_goal_state,
    merge_resolved_params_with_session_answers,
    update_session_from_router_goal,
    build_guided_reference_readiness,
)
```

## Runtime / Security Contract Notes

- preserve router goal bootstrap semantics and current `guided_handoff` usage
- preserve router goal reset semantics and partial-answer reuse for
  `router_clear_goal(...)` / `router_set_goal(...)`
- keep required/preferred prompt bundles unchanged for the same phase/domain
  inputs
- preserve reference-readiness blocking reasons and payload vocabulary

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`
- `tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py`
- `tests/e2e/router/test_guided_manual_handoff.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_session_phase.py tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py tests/e2e/router/test_guided_manual_handoff.py -q`

## Docs To Update

- `_docs/_PROMPTS/README.md` only if internal prompt-bundle ownership wording
  changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- goal bootstrap and prompt-bundle helpers no longer live inline with unrelated
  state/persistence logic
- goal reset and partial-answer merge helpers have an explicit home instead of
  remaining an unowned remainder in the monolith
- router/manual handoff and prompt recommendations remain behaviorally identical
- reference-readiness payloads stay stable across guided sessions

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
