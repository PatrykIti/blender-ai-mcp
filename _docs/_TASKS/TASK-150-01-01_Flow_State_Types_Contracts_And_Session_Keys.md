# TASK-150-01-01: Flow State Types, Contracts, And Session Keys

**Parent:** [TASK-150-01](./TASK-150-01_Guided_Flow_State_Contract_And_Session_Model.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define the typed `guided_flow_state` envelope, contract models, and session
storage keys used by the server-driven guided flow layer.

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/contracts/router.py`
- `server/adapters/mcp/contracts/reference.py`
- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`

## Planned File Work

- Modify:
  - `server/adapters/mcp/session_capabilities.py`
  - `server/adapters/mcp/contracts/router.py`
  - `server/adapters/mcp/contracts/reference.py`
  - `tests/unit/adapters/mcp/test_session_phase.py`
  - `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- Create only if needed:
  - dedicated test file for `guided_flow_state` serialization or contract parity

## Detailed Implementation Notes

- extend `SessionCapabilityState` with a new `guided_flow_state` field instead
  of creating a parallel session object tree
- add one typed contract model in MCP contracts first, then mirror it into
  session storage
- keep the first version intentionally shallow:
  - strings / enums / tuples / plain dict items
  - no rich nested planner graph in the state contract
- ensure the state shape is stable enough that later leaves can read it from:
  - `router_set_goal(...)`
  - `router_get_status()`
  - visibility/search transforms

## Planned Test Files And Scenarios

- Modify `tests/unit/adapters/mcp/test_session_phase.py`
  - add one test that default session state carries `guided_flow_state is None`
  - add one test that session persistence round-trips a populated
    `guided_flow_state`
  - add one test that clearing/resetting guided goal state also clears
    `guided_flow_state`
- Modify `tests/unit/adapters/mcp/test_contract_payload_parity.py`
  - add one parity fixture proving `guided_flow_state` serializes in the public
    router payload with the expected field names
  - add one negative test that optional fields remain omitted/`None` cleanly
- Create `tests/unit/adapters/mcp/test_guided_flow_state_contract.py` if the
  existing parity tests become too crowded
  - schema-shape expectations
  - enum/value vocabulary expectations
  - regression for accidental field renames

## Example Test Sketch

```python
def test_session_capability_state_round_trips_guided_flow_state():
    state = SessionCapabilityState(
        phase=SessionPhase.PLANNING,
        guided_flow_state={
            "flow_id": "guided_default",
            "domain_profile": "generic",
            "current_step": "establish_spatial_context",
            "completed_steps": [],
            "required_checks": ["scene_scope_graph"],
            "required_prompts": ["guided_session_start"],
            "next_actions": ["run_required_checks"],
            "blocked_families": [],
            "step_status": "ready",
        },
    )
    set_session_capability_state(ctx, state)
    assert get_session_capability_state(ctx).guided_flow_state["current_step"] == "establish_spatial_context"
```

## Acceptance Criteria

- one machine-readable `guided_flow_state` envelope exists with typed fields
- session storage has explicit keys for the new flow-state fields
- the shape is reusable across `generic`, `creature`, and `building` overlays
- the contract leaves room for:
  - current step
  - completed steps
  - required checks
  - required prompts
  - next actions
  - blocked families

## Pseudocode Sketch

```python
@dataclass(frozen=True)
class GuidedFlowState:
    flow_id: str
    domain_profile: Literal["generic", "creature", "building"]
    current_step: str
    completed_steps: tuple[str, ...]
    required_checks: tuple[dict[str, Any], ...]
    required_prompts: tuple[str, ...]
    next_actions: tuple[str, ...]
    blocked_families: tuple[str, ...]
    step_status: Literal["ready", "blocked", "needs_checkpoint", "needs_validation"]

SESSION_GUIDED_FLOW_STATE_KEY = "guided_flow_state"

def get_session_capability_state(...):
    ...
    guided_flow_state=get_session_value(ctx, SESSION_GUIDED_FLOW_STATE_KEY)

def set_session_capability_state(...):
    ...
    set_session_value(ctx, SESSION_GUIDED_FLOW_STATE_KEY, state.guided_flow_state)
```

## Docs To Update

- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`

## Changelog Impact

- include in the parent TASK-150 changelog entry when shipped
