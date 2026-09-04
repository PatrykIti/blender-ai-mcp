# 237. Guided pair role cardinality

Date: 2026-04-14

## Summary

Completed TASK-156 by making guided creature pair roles cardinality-aware.

## What Changed

- added guided role cardinality metadata for creature pair roles:
  - `ear_pair`
  - `foreleg_pair`
  - `hindleg_pair`
- added compact guided flow diagnostics:
  - `role_counts`
  - `role_cardinality`
  - `role_objects`
- changed role completion logic so one side-specific sibling such as `Ear_L`
  no longer completes the whole `ear_pair` role
- preserved aggregate object compatibility, so a single plural object such as
  `Squirrel_Ears` can still satisfy the pair role when intentionally used as a
  combined pair mesh/blockout object
- execution policy now continues to allow the second sibling and blocks
  over-cardinality calls once the pair is complete
- updated MCP/prompt docs and TASK-156 closeout state

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py::test_pair_role_registration_requires_two_side_specific_objects_before_completion tests/unit/adapters/mcp/test_guided_flow_state_contract.py::test_secondary_role_registration_advances_creature_flow_to_checkpoint_iterate tests/unit/adapters/mcp/test_context_bridge.py::test_route_tool_call_report_blocks_third_object_for_completed_pair_role -q`
  - result on this machine: `3 passed`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_context_bridge.py -q`
  - result on this machine: `43 passed`
