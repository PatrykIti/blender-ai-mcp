# TASK-168-03: Session Manifest, Prompt Priority, And Memory Drift Containment

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-168](./TASK-168_Profile_Bound_Orchestrator_Shielding_Feedback_And_Memory_Containment.md)
**Objective:** Surface one runtime-owned profile/session manifest and prompt-priority model that can outweigh stale external `memory.md`, old prompt stacks, and inherited tool-schema drift on `llm-guided`.
**Repository Touchpoints:** `server/adapters/mcp/session_capabilities_state.py`, `server/adapters/mcp/areas/router.py`, `server/adapters/mcp/contracts/router.py`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/prompts/prompt_catalog.py`, `server/adapters/mcp/prompts/rendering.py`, `server/adapters/mcp/prompts/provider.py`, `_docs/_PROMPTS/README.md`, `_docs/_PROMPTS/GUIDED_SESSION_START.md`, `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`, `_docs/_PROMPTS/REFERENCE_GUIDED_ARCHITECTURE_BUILD.md`, `_docs/_MCP_SERVER/README.md`, `tests/unit/adapters/mcp/test_prompt_catalog.py`, `tests/unit/adapters/mcp/test_prompt_provider.py`, `tests/unit/adapters/mcp/test_public_surface_docs.py`, `tests/unit/router/application/test_router_contracts.py`, `tests/e2e/integration/test_guided_surface_contract_parity.py`
**Acceptance Criteria:**
- the server can expose one compact runtime-owned profile/session contract that says what surface, phase, and guardrails are currently authoritative
- prompt assets and dynamic recommendations explicitly say that live runtime/profile contract outranks stale external memory and old tool schemas
- the session manifest stays read-only and compact; it is not a second public workflow tool
- prompt recommendations for creature/reference-guided flows prioritize the active runtime contract and compare cadence over free-form modeling heuristics

## Implementation Notes

- this task does **not** try to disable external controller memory globally
- the repo-owned answer is to make the live contract:
  - visible
  - short
  - repeated
  - higher priority than stale memory
- likely fields:
  - `surface_profile`
  - `contract_version`
  - `current_phase`
  - `current_step`
  - `allowed_families`
  - `allowed_roles`
  - `forbidden_patterns`
  - `next_action_mode`
- `forbidden_patterns` should cover the observed regressions:
  - hidden-tool guessing
  - continuing to mutate in `checkpoint_iterate`
  - `guided_role="eye_pair"`
  - legacy `label` / `notes` on staged compare
  - `contact_axis` / `contact_side` / signed `normal_axis`
- keep the live session-owned fields on `SessionCapabilityState` and the
  surfaced `router_get_status(...)` contract as the runtime authority; prompt
  assets only reinforce that authority

## Pseudocode

```python
session_manifest = {
    "surface_profile": "llm-guided",
    "current_phase": "build",
    "current_step": "checkpoint_iterate",
    "allowed_families": ["checkpoint_iterate", "reference_context", "spatial_context"],
    "forbidden_patterns": [
        "guided_role=eye_pair",
        "reference_compare_stage_checkpoint(label=..., notes=...)",
        "mutating build calls before compare loop completes",
    ],
}
```

## Runtime / Security Contract Notes

- runtime/profile manifest must never expose secrets, local auth material, or hidden/internal inventory
- prompt assets may reinforce the manifest, but must not become the primary enforcement layer
- session manifest is informative and normative for the controller, not a write surface

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_prompt_provider.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_ARCHITECTURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- historical closeout entry ownership belongs to
  [TASK-168-04](./TASK-168-04_Profile_Contract_Rewrite_Validation_And_Closeout.md)

## Status / Board Update

- remains nested under `TASK-168`
- should close before final docs/closeout claims a stable anti-drift controller contract

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_prompt_catalog.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_prompt_provider.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/router/application/test_router_contracts.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py -q`

## Validation Category

- prompt/provider unit tests
- `git diff --check`
