# 284. TASK-145 validation and regression hardening

Date: 2026-05-01
Version: -

## Summary

- aligned rich `planner_detail.detail_trimmed` with staged
  `budget_control.detail_trimmed` so planner detail no longer overstates
  completeness when compare evidence was trimmed
- expanded unit coverage for:
  - compact iterate nested debug-payload stripping
  - compare/iterate `planner_detail` contract parity
  - fail-closed guided mutator behavior with executor non-execution proof
- added Blender-backed E2E proof for:
  - truth-driven assembly planner routing on staged compare
  - rich sculpt-ready planner detail on a real stage compare
- repaired the stdio guided-surface parity harness so `guided_register_part`
  validates against the same fake scene-object registry that the harness uses
  for primitive creation

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_context_bridge.py -q`
  - result on this machine: `117 passed`
- `poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_guided_surface_benchmarks.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_prompt_catalog.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
  - result on this machine: `252 passed`
- `poetry run pytest tests/e2e/integration/test_guided_streamable_spatial_support.py tests/e2e/integration/test_guided_surface_contract_parity.py tests/e2e/vision/test_reference_stage_truth_handoff.py tests/e2e/vision/test_reference_guided_creature_comparison.py tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py tests/e2e/tools/macro/test_macro_attach_part_to_surface.py tests/e2e/tools/macro/test_macro_align_part_with_contact.py tests/e2e/tools/sculpt/test_sculpt_tools.py -q -rs`
  - result on this machine: `34 passed`
- `poetry run ruff check server/adapters/mcp/areas/reference.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_context_bridge.py tests/e2e/vision/test_reference_stage_truth_handoff.py tests/e2e/integration/test_guided_surface_contract_parity.py`
  - result on this machine: passed
- `poetry run mypy server/adapters/mcp/areas/reference.py server/adapters/mcp/contracts/reference.py server/adapters/mcp/router_helper.py`
  - result on this machine: passed
- `poetry run pytest tests/unit --collect-only -q`
  - result on this machine: `3158 tests collected`
- `poetry run pytest tests/e2e --collect-only -q`
  - result on this machine: `429 tests collected`
