# TASK-166-05-02: Runtime Diagnostics And Fail-Safe Budget Caps

**Parent:** [TASK-166-05](./TASK-166-05_Configurable_Vision_Assist_Budgets_And_Runtime_Overrides.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Surface configured and effective compare budgets in diagnostics while keeping fail-safe caps that prevent accidental unbounded payloads.

## Repository Touchpoints

- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/vision/runner.py`
- `server/adapters/mcp/sampling/result_types.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/reference_planner.py`
- `server/adapters/mcp/areas/reference_feedback.py`
- `server/adapters/mcp/contracts/reference.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`

## Implementation Notes

- Surface configured vs effective budget values through the existing
  `budget_control` seam and any additive `compare_diagnostics` field without
  making clients parse raw runner internals.
- Keep the staged compare assembler, planner budget helpers, and compact
  feedback projection aligned on one typed configured-vs-effective budget
  picture rather than recomputing ad-hoc diagnostics per caller.
- Keep fail-safe upper bounds explicit so operators can distinguish
  configured-budget intent from clipped effective runtime behavior.
- If budget clipping changes the next safe action, the compact
  `reference_orchestrator_feedback` projection should carry that as bounded
  uncertainty rather than a hidden transport-only detail.

## Acceptance Criteria

- runtime diagnostics show configured vs effective compare budgets
- hard safety caps still prevent pathological payload growth
- per-run budget detail can surface additively in richer compare diagnostics
  while `budget_control` remains the existing top-level operator surface

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_runner.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py` when budget
  diagnostics change a client-visible staged contract

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- include in the umbrella `_docs/_CHANGELOG/` entry when budget diagnostics and
  fail-safe caps ship

## Status / Board Update

- keep parent `TASK-166` and this leaf aligned when budget diagnostics close or
  remain explicit follow-on work

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runner.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/router/application/test_router_contracts.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
