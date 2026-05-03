# TASK-159-04-01: Session Capability State Model And Persistence Split

**Parent:** [TASK-159-04](./TASK-159-04_Session_Capabilities_Modularization_And_Guided_State_Boundaries.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Separate the session-capability dataclasses, normalization helpers, and sync/async
persistence seam from the rest of `session_capabilities.py` while keeping the
module import facade stable.

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- likely new helper module such as `server/adapters/mcp/session_capabilities_state.py`
- `server/adapters/mcp/session_state.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/unit/adapters/mcp/test_session_phase.py`

## Current Code Anchors

- `SessionCapabilityState`
- `GuidedReferenceReadinessState`
- `_normalize_guided_flow_state(...)`
- `_normalize_gate_plan(...)`
- `get_session_capability_state(...)`
- `get_session_capability_state_async(...)`
- `set_session_capability_state(...)`
- `set_session_capability_state_async(...)`

## Planned Code Shape

```python
from .session_capabilities_state import (
    SessionCapabilityState,
    get_session_capability_state,
    set_session_capability_state,
)
```

## Runtime / Security Contract Notes

- keep current session-key vocabulary, normalization rules, and no-cross-session
  leakage guarantees
- preserve paired sync/async persistence behavior
- do not change which session keys are written or how typed contracts are rebuilt
  from raw session storage

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/unit/adapters/mcp/test_session_phase.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_session_phase.py -q`

## Docs To Update

- inherit parent docs closeout unless session-state ownership wording changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- state model and persistence helpers have a bounded home outside the monolith
- session serialization/deserialization semantics remain unchanged
- the facade still exports the same state access functions used elsewhere in the
  repo

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
