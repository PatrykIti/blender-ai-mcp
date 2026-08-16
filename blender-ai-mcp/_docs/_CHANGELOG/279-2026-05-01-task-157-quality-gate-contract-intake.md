# 279. TASK-157 quality-gate contract and intake

Date: 2026-05-01

## Summary

- added `server/adapters/mcp/contracts/quality_gates.py` as the v1
  goal-derived quality-gate contract module
- introduced typed proposal, normalized gate, gate-plan, evidence requirement,
  evidence ref, source provenance, policy warning, domain template, and intake
  result contracts
- added session-scoped `gate_plan` persistence beside `guided_flow_state`
- added optional `gate_proposal` intake on `router_set_goal(...)`, returning
  `active_gate_plan` and `gate_intake_result`
- exposed `active_gate_plan` through `router_get_status(...)`,
  `router_set_goal(...)`, `reference_compare_stage_checkpoint(...)`, and
  `reference_iterate_stage_checkpoint(...)`
- kept LLM, reference-understanding, silhouette, segmentation,
  classification, and VLM checkpoint sources advisory only; normalized gates
  start as `pending` until later deterministic verifier slices update status
- updated README, MCP docs, available tools, prompt guidance, router
  responsibility boundaries, and TASK-157 board/task state

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_contracts.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py -v`
