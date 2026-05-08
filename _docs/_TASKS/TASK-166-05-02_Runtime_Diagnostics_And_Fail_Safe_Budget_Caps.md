# TASK-166-05-02: Runtime Diagnostics And Fail-Safe Budget Caps

**Parent:** [TASK-166-05](./TASK-166-05_Configurable_Vision_Assist_Budgets_And_Runtime_Overrides.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Surface configured and effective compare budgets in diagnostics while keeping fail-safe caps that prevent accidental unbounded payloads.

## Repository Touchpoints

- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/vision/runner.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/reference_feedback.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`

## Implementation Notes

- Surface configured vs effective budget values through the existing
  `budget_control` seam and any additive `compare_diagnostics` field without
  making clients parse raw runner internals.
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
- `tests/e2e/integration/test_guided_gate_state_transport.py` when budget
  diagnostics change a client-visible staged contract

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runner.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
