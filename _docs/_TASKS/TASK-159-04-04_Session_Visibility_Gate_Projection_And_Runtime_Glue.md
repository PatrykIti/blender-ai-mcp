# TASK-159-04-04: Session Visibility, Gate Projection, And Runtime Glue

**Parent:** [TASK-159-04](./TASK-159-04_Session_Capabilities_Modularization_And_Guided_State_Boundaries.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Extract visibility refresh, gate projection, and the router/search/prompt glue
that consumes session-capability state while preserving request-path runtime
behavior on stdio and Streamable HTTP.

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- likely new helper module such as `server/adapters/mcp/session_capabilities_runtime_glue.py`
- `server/adapters/mcp/guided_mode.py`
- `server/adapters/mcp/discovery/search_surface.py`
- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/prompts/provider.py`
- `server/adapters/mcp/transforms/quality_gate_verifier.py`
- `tests/unit/adapters/mcp/test_quality_gate_verifier.py`
- `tests/unit/adapters/mcp/test_quality_gate_intake.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/router/test_guided_manual_handoff.py`

## Current Code Anchors

- `update_quality_gate_plan_from_relation_graph(...)`
- `verify_gate_plan_with_relation_graph(...)`
- `record_router_execution_outcome(...)`
- `refresh_visibility_for_session_state(...)`
- `apply_visibility_for_session_state(...)`
- `mark_guided_spatial_state_stale(...)`
- `mark_guided_spatial_state_stale_async(...)`

## Planned Code Shape

```python
from .session_capabilities_runtime_glue import (
    apply_visibility_for_session_state,
    update_quality_gate_plan_from_relation_graph,
)
```

## Runtime / Security Contract Notes

- preserve the active-request-path visibility rules documented in
  `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- preserve deterministic relation-graph gate verification on the existing
  verifier seam rather than turning semantic/runtime glue into the authority
- do not reintroduce detached session writes or background visibility refreshes
  for paths that currently rely on awaited completion
- keep search/router/prompt consumers behaviorally identical for the same guided
  state and gate plan

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_quality_gate_verifier.py`
- `tests/unit/adapters/mcp/test_quality_gate_intake.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/router/test_guided_manual_handoff.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_router_elicitation.py tests/e2e/integration/test_guided_surface_contract_parity.py tests/e2e/integration/test_guided_gate_state_transport.py tests/e2e/router/test_guided_manual_handoff.py -q`

## Docs To Update

- `_docs/_MCP_SERVER/README.md` or `_docs/_PROMPTS/README.md` only if runtime
  glue ownership wording changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- visibility/gate/runtime glue no longer shares one edit zone with unrelated
  state and registry logic
- search/router/prompt/runtime consumers continue to observe the same guided
  behavior
- gate projection continues to use the same deterministic verifier-backed
  relation-graph semantics
- transport-backed tests still prove no request-path visibility regression

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
