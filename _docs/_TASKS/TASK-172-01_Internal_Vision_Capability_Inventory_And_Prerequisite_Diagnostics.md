# TASK-172-01: Internal Vision Capability Inventory And Prerequisite Diagnostics

**Parent:** [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Add one canonical typed internal capability-inventory model and additive prerequisite-diagnostics seam for optional perception/runtime branches without inventing a second public capability system or new MCP discovery flow.
**Repository Touchpoints:** `server/adapters/mcp/vision/config.py`, `server/adapters/mcp/vision/runtime.py`, `server/adapters/mcp/vision/backends.py`, `server/adapters/mcp/vision/runner.py`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/contracts/router.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/session_capabilities_state.py`, `server/adapters/mcp/sampling/result_types.py`, `server/infrastructure/config.py`, `tests/unit/adapters/mcp/test_vision_runtime_config.py`, `tests/unit/adapters/mcp/test_vision_runner.py`, `tests/unit/adapters/mcp/test_vision_external_backend.py`, `tests/unit/adapters/mcp/test_vision_result_types.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/unit/router/application/test_router_contracts.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `_docs/_VISION/README.md`, `_docs/_MCP_SERVER/README.md`
**Acceptance Criteria:**
- the runtime has one canonical typed internal capability-inventory model for optional capability status, provider identity, prerequisite summary, activation scope, and reuse/lifecycle class
- operator/client-visible diagnostics remain additive on existing surfaces and do not create a new public capability tool
- missing optional heavy capability reports enhancement/unavailable state without blocking normal guided/reference flow

## Implementation Notes

- treat `TASK-140-06` as the substrate owner for external model capabilities;
  this leaf should consume and extend that capability discipline rather than
  duplicating the OpenRouter-specific work
- align public capability summaries with the already-shipped
  `VisionCapabilitySummaryContract` / `VisionAssistContract` diagnostics lane
  instead of creating a second operator-facing capability story
- if readiness becomes operator-visible outside compare/iterate payloads, use
  `RouterStatusContract` / `router_get_status(...)` rather than inventing a new
  status surface
- cover at least these runtime-owned capability classes:
  - external vision model capabilities
  - reference classifier
  - packet-local segmentation
  - packet-local part localization
- keep the inventory internal/runtime-facing; public surfaces should only expose
  bounded diagnostics such as prerequisite hints, unavailable notes, or
  capability summaries where needed
- do not overload FastMCP platform capability/discovery surfaces for this work
- if a new typed public field is needed, prefer a small additive contract on
  existing compare/iterate or status surfaces instead of a new top-level tool
- likely owner shape:
  - `VisionOptionalCapabilityState`
  - `VisionOptionalCapabilityInventory`
  - one runtime helper that renders bounded diagnostics from that inventory

## Pseudocode

```python
inventory = [
    capability("external_model", status="available", source="openrouter_api"),
    capability("reference_classifier", status="disabled", optional=True),
    capability("part_segmentation", status="available", optional=True),
    capability("part_localization", status="missing", optional=True),
]

feedback = build_optional_capability_diagnostics(
    inventory=inventory,
    current_scope="checkpoint_iterate",
)
```

## Runtime / Security Contract Notes

- diagnostics must be secret-safe and must not leak API keys, local paths, or
  raw sidecar payloads
- unavailable optional capability must not mutate guided state or gate status
- inventory fields should separate:
  - availability
  - capability source
  - prerequisite state
  - lifecycle / reuse class

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_runner.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md` when operator-facing
  diagnostics/config examples change

## Changelog Impact

- include in the first `TASK-172` implementation changelog entry when this leaf
  lands

## Status / Board Update

- board tracking remains on the umbrella `TASK-172`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_runner.py tests/unit/adapters/mcp/test_vision_external_backend.py tests/unit/adapters/mcp/test_vision_result_types.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/router/application/test_router_contracts.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Validation Category

- runtime diagnostics and typed config proof
