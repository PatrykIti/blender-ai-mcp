# TASK-159-04: Session Capabilities Modularization And Guided State Boundaries

**Parent:** [TASK-159](./TASK-159_Modularize_Oversized_Guided_Runtime_And_Scene_Owner_Files.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Split `server/adapters/mcp/session_capabilities.py` into clearer responsibility
modules for:

- guided_state
- visibility_refresh
- quality_gate_projection
- prompt_bundle_selection

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
  - `session_capabilities_guided_state.py`
  - `session_capabilities_visibility_refresh.py`
  - `session_capabilities_quality_gates.py`
  - `session_capabilities_prompt_bundles.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/prompts/`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`
- `tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`

## Implementation Notes

- Keep `session_capabilities.py` as the stable import facade at first.
- Move internal helpers and mutation logic by concern into sibling modules.
- Preserve existing sync/async paired behavior where both paths exist today.
- Preserve current public state vocabulary:
  - `guided_flow_state`
  - `active_gate_plan`
  - required / preferred prompt bundles
  - spatial freshness / scope fingerprints
- Do not quietly change when visibility refreshes, when gates become stale, or
  when prompt bundles are emitted; those are runtime behaviors, not formatting.

## Pseudocode

```python
# stable facade module
from .session_capabilities_guided_state import build_initial_guided_flow_state
from .session_capabilities_visibility_refresh import refresh_visibility_for_state
from .session_capabilities_quality_gates import update_quality_gate_plan_from_relation_graph
from .session_capabilities_prompt_bundles import build_required_prompt_bundle

__all__ = [
    "build_initial_guided_flow_state",
    "refresh_visibility_for_state",
    "update_quality_gate_plan_from_relation_graph",
    "build_required_prompt_bundle",
]
```

## Runtime / Security Contract Notes

- Preserve current session isolation and no-cross-session leakage guarantees.
- Preserve current guided-state and visibility-refresh behavior on both stdio
  and Streamable HTTP paths.
- Do not let refactor work become an excuse to detach session writes from the
  active request path where the runtime currently relies on synchronous or
  awaited completion.

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`
- `tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py tests/unit/adapters/mcp/test_context_bridge.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py tests/e2e/integration/test_guided_gate_state_transport.py -q`

## Docs To Update

- `_docs/_MCP_SERVER/README.md` only if internal ownership wording needs maintenance
- `_docs/_PROMPTS/README.md` only if prompt-bundle shaping notes depend on internal owner names
- `_docs/_TASKS/README.md` only when the task status changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- `session_capabilities.py` is reduced to a stable facade/re-export role plus
  any truly central glue that still needs one entry module
- guided-state, visibility-refresh, gate-projection, and prompt-bundle logic
  have clearer internal ownership seams
- guided runtime behavior remains stable across unit and transport/integration
  lanes
- future guided-runtime work no longer has to land by default in one monolithic
  file

## Status / Board Update

- keep promoted tracking on the parent `TASK-159`
- do not promote this slice independently unless it becomes the only remaining
  open branch in the family
