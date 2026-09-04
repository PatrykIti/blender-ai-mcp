# 285. TASK-157 runtime drift alignment

Date: 2026-05-01

## Summary

- aligned goal-time `TASK-157` gate intake with the existing policy surface by
  dropping gates that require unavailable reference/perception evidence on the
  current `router_set_goal(..., gate_proposal=...)` path and returning a typed
  policy warning instead of silently accepting the drift
- narrowed guided gate invalidation to affected objects when the existing
  mutation/report seams can provide that scope, instead of staling every
  verifier-backed gate after any successful mutation
- kept `router_get_status(...)` visibility diagnostics in sync with the already
  applied gate-aware session surface by passing the active `gate_plan` through
  the same diagnostics builder
- extended the first deterministic verifier slice with `symmetry_pair`
  evaluation on top of existing `scene_relation_graph(...)` symmetry semantics
  and bounded symmetry repair tools
- made `reference_iterate_stage_checkpoint(...)` respect unresolved
  `completion_blockers` when choosing `loop_disposition`, so gate blockers can
  escalate the loop to `inspect_validate` without inventing a parallel flow
- refreshed the main TASK-157 docs and test guidance so the shipped slice stays
  aligned with the live contract and the open Blender-backed regression proof
  remains clearly tracked under `TASK-157-04`

## Validation

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_router_elicitation.py tests/unit/adapters/mcp/test_context_bridge.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_contracts.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py -q`
- `poetry run pytest tests/e2e/integration/test_guided_inspect_validate_handoff.py -q`
