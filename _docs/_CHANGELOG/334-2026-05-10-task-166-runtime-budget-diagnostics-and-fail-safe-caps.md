# 334. TASK-166 runtime budget diagnostics and fail-safe caps

Date: 2026-05-10
Task: `TASK-166-05-02`

## Summary

- added explicit bounded vision fail-safe caps for image count, serialized input
  characters, and output tokens
- kept configured runtime budget intent visible while routing runner/backend and
  staged compare execution through effective clipped limits
- extended staged `budget_control` and compact
  `reference_orchestrator_feedback` so fail-safe clipping is visible without
  parsing raw runner internals
- aligned the OpenRouter helper default token budget with the new fail-safe cap

## Validation

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_runner.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
