# 276. TASK-145 repair planner and sculpt handoff

Date: 2026-04-30
Version: -

## Summary

- added compact `planner_summary` and rich-profile `planner_detail` to staged
  reference compare/iterate contracts
- extended `refinement_route` and `refinement_handoff` with target scope,
  source-class provenance, typed blockers, handoff state, and bounded sculpt
  eligibility metadata
- made staged sculpt readiness fail closed on missing or blocking view
  diagnostics by returning a `scene_view_diagnostics(...)` precondition instead
  of treating vision prose as sculpt readiness
- included `sculpt_crease_region` in the deterministic planner-driven sculpt
  recommendation subset while keeping sculpt hidden on default `llm-guided`
  surfaces
- extended guided execution fail-closed behavior so unmapped `sculpt_*`
  mutators cannot run under an active guided family contract
- updated MCP, prompt, vision, router, and tool-inventory docs for the
  planner-first read order and recommendation-only sculpt handoff

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_guided_surface_benchmarks.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_prompt_catalog.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
  - result on this machine: `244 passed`
- `poetry run ruff check server/adapters/mcp/areas/reference.py server/adapters/mcp/contracts/reference.py server/adapters/mcp/router_helper.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_context_bridge.py`
  - result on this machine: passed
- `poetry run mypy server/adapters/mcp/areas/reference.py server/adapters/mcp/contracts/reference.py server/adapters/mcp/router_helper.py`
  - result on this machine: passed
- `poetry run pytest tests/e2e/vision/test_reference_stage_truth_handoff.py tests/e2e/tools/sculpt/test_sculpt_tools.py -q -rs`
  - result on this machine: `19 skipped` because Blender / Blender RPC was not available
