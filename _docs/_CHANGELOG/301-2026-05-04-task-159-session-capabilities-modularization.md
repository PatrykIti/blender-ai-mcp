# 301. TASK-159 session capabilities modularization

Date: 2026-05-04

## Summary

- completed `TASK-159-04` by splitting the oversized guided runtime owner file
  `server/adapters/mcp/session_capabilities.py` into focused modules:
  - `server/adapters/mcp/session_capabilities_state.py`
  - `server/adapters/mcp/session_capabilities_flow.py`
  - `server/adapters/mcp/session_capabilities_bootstrap.py`
  - `server/adapters/mcp/session_capabilities_registry.py`
  - `server/adapters/mcp/session_capabilities_runtime_glue.py`
- reduced `server/adapters/mcp/session_capabilities.py` to a stable facade plus
  the few wrapper seams that still need repo-level patch points:
  - sync visibility refresh
  - Blender object-name validation for guided rename paths
  - sync/async guided visibility callback injection used by existing tests and
    request-path runtime behavior
- kept the guided runtime contract stable for:
  - session persistence and normalization
  - router goal bootstrap and prompt bundles
  - guided part registry and flow transitions
  - gate intake, relation-graph projection, and visibility refresh
- closed task docs for `TASK-159-04` and leaves `TASK-159-04-01` through
  `TASK-159-04-04` while leaving umbrella `TASK-159` open for the remaining
  monolithic files (`reference.py`, MCP `scene.py`, and addon `scene.py`)

## Validation

- `python3 -m py_compile server/adapters/mcp/session_capabilities.py server/adapters/mcp/session_capabilities_state.py server/adapters/mcp/session_capabilities_flow.py server/adapters/mcp/session_capabilities_bootstrap.py server/adapters/mcp/session_capabilities_registry.py server/adapters/mcp/session_capabilities_runtime_glue.py`
- `poetry run ruff check server/adapters/mcp/session_capabilities.py server/adapters/mcp/session_capabilities_state.py server/adapters/mcp/session_capabilities_flow.py server/adapters/mcp/session_capabilities_bootstrap.py server/adapters/mcp/session_capabilities_registry.py server/adapters/mcp/session_capabilities_runtime_glue.py`
- `poetry run mypy server/adapters/mcp/session_capabilities.py server/adapters/mcp/session_capabilities_state.py server/adapters/mcp/session_capabilities_flow.py server/adapters/mcp/session_capabilities_bootstrap.py server/adapters/mcp/session_capabilities_registry.py server/adapters/mcp/session_capabilities_runtime_glue.py`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py tests/unit/adapters/mcp/test_session_phase.py tests/unit/router/application/test_session_phase_hints.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_router_elicitation.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/router/application/test_router_contracts.py tests/unit/adapters/mcp/test_reference_images.py -q`
  - result on this machine: `342 passed`
- outside sandbox:
  - `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py tests/e2e/integration/test_guided_gate_state_transport.py tests/e2e/router/test_guided_manual_handoff.py -q`
  - result on this machine: `19 passed`
