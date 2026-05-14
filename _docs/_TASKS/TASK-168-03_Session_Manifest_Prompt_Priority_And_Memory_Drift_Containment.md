# TASK-168-03: Session Manifest, Prompt Priority, And Memory Drift Containment

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-168](./TASK-168_Profile_Bound_Orchestrator_Shielding_Feedback_And_Memory_Containment.md)
**Objective:** Surface one runtime-owned profile/session authority line through the existing `router_get_status(...)`, `guided_flow_state`, `reference_orchestrator_feedback`, and prompt surfaces so live runtime state can outweigh stale external `memory.md`, old prompt stacks, and inherited tool-schema drift on `llm-guided`.
**Repository Touchpoints:** `server/adapters/mcp/session_capabilities_state.py`, `server/adapters/mcp/areas/router.py`, `server/adapters/mcp/contracts/router.py`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/surfaces.py`, `server/adapters/mcp/prompts/prompt_catalog.py`, `server/adapters/mcp/prompts/rendering.py`, `server/adapters/mcp/prompts/provider.py`, `_docs/_PROMPTS/README.md`, `_docs/_PROMPTS/GUIDED_SESSION_START.md`, `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`, `_docs/_PROMPTS/REFERENCE_GUIDED_ARCHITECTURE_BUILD.md`, `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`, `_docs/_MCP_SERVER/README.md`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/unit/adapters/mcp/test_prompt_catalog.py`, `tests/unit/adapters/mcp/test_prompt_provider.py`, `tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py`, `tests/unit/adapters/mcp/test_public_surface_docs.py`, `tests/unit/router/application/test_router_contracts.py`, `tests/e2e/integration/test_guided_surface_contract_parity.py`
**Acceptance Criteria:**
- the server can expose one compact runtime-owned authority projection through
  existing router status fields such as `surface_profile`, `current_phase`, and
  `contract_version` plus the machine-readable `guided_flow_state` and
  `reference_orchestrator_feedback` seams
- prompt assets and dynamic recommendations explicitly say that live runtime/profile contract outranks stale external memory and old tool schemas
- the session manifest stays read-only and compact; it is a projection on the
  existing status/feedback seams, not a second public workflow tool or
  parallel wrapper
- prompt recommendations for creature/reference-guided flows prioritize the active runtime contract and compare cadence over free-form modeling heuristics

## Implementation Notes

- this task does **not** try to disable external controller memory globally
- the repo-owned answer is to make the live contract:
  - visible
  - short
  - repeated
  - higher priority than stale memory
- "session manifest" here means a compact authority projection on the existing
  `router_get_status(...)` surface, not a second top-level public wrapper
- likely authority lines on `router_get_status(...)` and companion guided
  surfaces:
  - `surface_profile`
  - `contract_version`
  - `current_phase`
  - `guided_flow_state.current_step`
  - `guided_flow_state.allowed_families`
  - `guided_flow_state.allowed_roles`
  - `guided_flow_state.required_checks`
  - `reference_orchestrator_feedback.next_actions`
  - `reference_orchestrator_feedback.next_checkpoint_tool`
  - `reference_orchestrator_feedback.blocking_reasons`
- prompt/runtime examples should explicitly call out the observed regressions,
  but scope them to exact tool signatures:
  - hidden-tool guessing
  - continuing to mutate in `checkpoint_iterate` before the compare loop
    completes unless the live active-workset / required-role exception is still
    open
  - `guided_role="eye_pair"`
  - legacy `label` / `notes` on staged compare
  - `macro_align_part_with_contact(contact_axis=..., contact_side=...)`
  - signed `normal_axis` values such as `-Y`
- keep the live session-owned fields on `SessionCapabilityState` and the
  surfaced `router_get_status(...)` contract as the runtime authority; prompt
  assets only reinforce that authority

## Pseudocode

```python
status_authority = {
    "surface_profile": status.surface_profile,
    "contract_version": status.contract_version,
    "current_phase": status.current_phase,
    "current_step": status.guided_flow_state.current_step,
    "allowed_families": status.guided_flow_state.allowed_families,
    "allowed_roles": status.guided_flow_state.allowed_roles,
    "required_checks": status.guided_flow_state.required_checks,
    "blocking_reasons": status.reference_orchestrator_feedback.blocking_reasons,
    "next_actions": status.reference_orchestrator_feedback.next_actions,
    "next_checkpoint_tool": status.reference_orchestrator_feedback.next_checkpoint_tool,
}
```

## Runtime / Security Contract Notes

- runtime/profile manifest must never expose secrets, local auth material, or hidden/internal inventory
- prompt assets may reinforce the manifest, but must not become the primary enforcement layer
- session manifest is informative and normative for the controller, not a write surface

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_prompt_provider.py`
- `tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_ARCHITECTURE_BUILD.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- historical closeout entry ownership belongs to
  [TASK-168-04](./TASK-168-04_Profile_Contract_Rewrite_Validation_And_Closeout.md)

## Status / Board Update

- remains nested under `TASK-168`
- should close before final docs/closeout claims a stable anti-drift controller contract

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_prompt_catalog.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_prompt_provider.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/router/application/test_router_contracts.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`

## Validation Category

- session/router/prompt unit tests plus repo-supported Blender E2E proof
- `git diff --check`
