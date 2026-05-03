# TASK-159-04: Session Capabilities Modularization And Guided State Boundaries

**Parent:** [TASK-159](./TASK-159_Modularize_Oversized_Guided_Runtime_And_Scene_Owner_Files.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Split `server/adapters/mcp/session_capabilities.py` into clearer responsibility
modules for:

- session_state_model_and_persistence
- goal_bootstrap_and_prompt_bundle_selection
- guided_part_registry_and_flow_transitions
- visibility_refresh_and_gate_projection_runtime_glue

while keeping `server.adapters.mcp.session_capabilities` as the stable facade
import surface for the rest of the repo.

## Business Problem

`session_capabilities.py` now owns too much of the live guided runtime:

- session-state persistence and mutation
- guided-flow construction
- spatial freshness and rearm bookkeeping
- visibility refresh triggers and policy helpers
- gate-plan refresh / projection hooks
- prompt-bundle selection and required-check shaping

That file has become the central gravity well for guided runtime behavior.
Leaving it monolithic increases the chance that:

- one gate/state fix regresses visibility refresh
- one prompt-bundle change regresses guided-flow construction
- future transport/session work becomes harder because every edit touches the
  same long file
- future contributors start adding more mixed concerns there because no smaller
  internal seams exist

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- likely new sibling modules such as:
  - `session_capabilities_state.py`
  - `session_capabilities_bootstrap.py`
  - `session_capabilities_registry.py`
  - `session_capabilities_runtime_glue.py`
- `server/adapters/mcp/session_state.py`
- `server/adapters/mcp/guided_mode.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/router/application/session_phase_hints.py`
- `server/adapters/mcp/discovery/search_surface.py`
- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/prompts/`
- `server/adapters/mcp/prompts/provider.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/unit/router/application/test_session_phase_hints.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`
- `tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/router/test_guided_manual_handoff.py`

## Implementation Notes

- Keep `session_capabilities.py` as the stable import facade at first.
- Move internal helpers and mutation logic by concern into sibling modules.
- Preserve existing sync/async paired behavior where both paths exist today.
- Preserve current public state vocabulary:
  - `guided_flow_state`
  - `gate_plan`
  - required / preferred prompt bundles
  - spatial freshness / scope fingerprints
- Keep router bootstrap, search/discovery refresh, prompt-provider consumption,
  reference-readiness adoption, and session persistence seams explicit in the
  plan rather than treating them as incidental callers.
- Do not quietly change when visibility refreshes, when gates become stale, or
  when prompt bundles are emitted; those are runtime behaviors, not formatting.

## Pseudocode

```python
# stable facade module
from .session_capabilities_state import (
    SessionCapabilityState,
    get_session_capability_state,
    set_session_capability_state,
)
from .session_capabilities_bootstrap import (
    _build_initial_guided_flow_state,
    _build_required_prompt_bundle,
)
from .session_capabilities_registry import register_guided_part_role
from .session_capabilities_runtime_glue import (
    refresh_visibility_for_session_state,
    update_quality_gate_plan_from_relation_graph,
)

__all__ = [
    "SessionCapabilityState",
    "get_session_capability_state",
    "set_session_capability_state",
    "update_quality_gate_plan_from_relation_graph",
    "refresh_visibility_for_session_state",
    "register_guided_part_role",
]
```

## Runtime / Security Contract Notes

- Preserve current session isolation and no-cross-session leakage guarantees.
- Preserve current guided-state and visibility-refresh behavior on both stdio
  and Streamable HTTP paths.
- Preserve the current request-path visibility application rules for native MCP
  requests; do not reintroduce detached or background visibility writes where
  the runtime currently relies on awaited completion.
- Do not let refactor work become an excuse to detach session writes from the
  active request path where the runtime currently relies on synchronous or
  awaited completion.

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-159-04-01](./TASK-159-04-01_Session_Capability_State_Model_And_Persistence_Split.md) | Separate the state dataclasses, normalization, and sync/async persistence seam behind the stable facade |
| 2 | [TASK-159-04-02](./TASK-159-04-02_Session_Goal_Bootstrap_Prompt_Bundles_And_Reference_Readiness.md) | Extract goal bootstrap, goal reset, partial-answer merge, domain-profile, prompt-bundle, and reference-readiness helpers without drifting router/bootstrap semantics |
| 3 | [TASK-159-04-03](./TASK-159-04-03_Session_Guided_Part_Registry_And_Flow_Transitions.md) | Separate guided part registry, role summaries, and flow-transition helpers into a bounded runtime slice |
| 4 | [TASK-159-04-04](./TASK-159-04-04_Session_Visibility_Gate_Projection_And_Runtime_Glue.md) | Isolate visibility refresh, gate projection, and router/search/prompt glue while preserving request-path runtime behavior |

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/unit/router/application/test_session_phase_hints.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_quality_gate_verifier.py`
- `tests/unit/adapters/mcp/test_quality_gate_intake.py`
- `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`
- `tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/router/test_guided_manual_handoff.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py tests/unit/adapters/mcp/test_session_phase.py tests/unit/router/application/test_session_phase_hints.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_router_elicitation.py tests/unit/adapters/mcp/test_search_surface.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py tests/e2e/integration/test_guided_gate_state_transport.py tests/e2e/router/test_guided_manual_handoff.py -q`

## Docs To Update

- `_docs/_MCP_SERVER/README.md` only if internal ownership wording needs maintenance
- `_docs/_PROMPTS/README.md` only if prompt-bundle shaping notes depend on internal owner names
- `_docs/_TASKS/README.md` only when the task status changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- `session_capabilities.py` is reduced to a stable facade/re-export role plus
  any truly central glue that still needs one entry module
- state persistence, goal bootstrap/prompt selection, guided part registry/flow
  transitions, and visibility/gate runtime glue have clearer internal ownership
  seams
- guided runtime behavior remains stable across unit and transport/integration
  lanes
- router/status, search/discovery, and prompt-provider consumers continue to see
  the same guided runtime semantics
- future guided-runtime work no longer has to land by default in one monolithic
  file

## Status / Board Update

- keep promoted tracking on the parent `TASK-159`
- execute this subtask through the leaves below so state/persistence, registry,
  and request-path visibility glue can be verified independently
- do not promote this slice independently unless it becomes the only remaining
  open branch in the family
