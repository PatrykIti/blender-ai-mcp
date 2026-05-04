# 293. TASK-158 reference-understanding runtime and harness path

Date: 2026-05-02

## Summary

- added a typed internal `ReferenceUnderstandingSummaryContract` on the shared
  `server/adapters/mcp/contracts/reference.py` owner instead of creating a new
  public MCP tool
- extended the shared vision prompt/parser/backend path so
  `request.metadata["mode"] == "reference_understanding"` uses a strict
  reference-understanding JSON contract with bounded family alias normalization
- added session-scoped `reference_understanding_summary` and
  `reference_understanding_gate_ids` persistence, and reused the closed
  `TASK-157` intake seam for advisory gate proposals instead of introducing a
  second reference-specific normalizer
- surfaced the typed reference-understanding summary on existing guided seams:
  `router_get_status(...)`, `reference_compare_stage_checkpoint(...)`, and
  `reference_iterate_stage_checkpoint(...)`
- kept optional perception on the existing default-off seam and added an
  explicit providerless `--fixture-only reference-understanding` path to
  `scripts/vision_harness.py` without changing the default backend-executing
  flow

## Validation

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_parsing.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/router/application/test_router_contracts.py tests/unit/scripts/test_script_tooling.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_router_elicitation.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py tests/e2e/integration/test_guided_gate_state_transport.py tests/e2e/integration/test_mcp_transport_modes.py -q`
