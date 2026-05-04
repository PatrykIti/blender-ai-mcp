# TASK-159-04-03: Session Guided Part Registry And Flow Transitions

**Parent:** [TASK-159-04](./TASK-159-04_Session_Capabilities_Modularization_And_Guided_State_Boundaries.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Separate guided part-registry, role-summary, and flow-transition helpers from
`session_capabilities.py` so future guided-runtime work stops defaulting to the
monolithic file.

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- likely new helper module such as `server/adapters/mcp/session_capabilities_registry.py`
- `server/adapters/mcp/router_helper.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_session_phase.py`

## Current Code Anchors

- `register_guided_part_role(...)`
- `rename_guided_part_registration(...)`
- `remove_guided_part_registrations(...)`
- `_apply_role_summary(...)`
- `_maybe_advance_guided_flow_from_part_registry_dict(...)`
- `_advance_guided_flow_for_iteration_dict(...)`
- `record_guided_flow_spatial_check_completion(...)`

## Planned Code Shape

```python
from .session_capabilities_registry import (
    register_guided_part_role,
    record_guided_flow_spatial_check_completion,
)
```

## Runtime / Security Contract Notes

- keep role-group vocabulary and guided flow transitions unchanged
- preserve router-facing registration side effects and dirtying behavior
- do not let registry extraction break session mutation ordering

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_session_phase.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_router_elicitation.py tests/unit/adapters/mcp/test_session_phase.py -q`

## Docs To Update

- inherit parent docs closeout unless guided flow/registry ownership wording
  changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- registry and flow-transition helpers have a bounded internal home
- router-facing guided runtime behavior remains unchanged
- unit tests still prove the same role-summary and flow-transition semantics

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
