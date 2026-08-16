# 300. TASK-160 guided client feedback and Streamable follow-up

Date: 2026-05-04

## Summary

- documented the already-landed guided-flow feedback stopgap for `llm-guided`
  client transitions:
  - `describe_guided_flow_feedback(...)` in
    `server/adapters/mcp/session_capabilities.py`
  - immediate `ctx_info(...)` feedback on async guided create/transform in
    `server/adapters/mcp/areas/modeling.py`
  - immediate guided-flow feedback appended to spatial support payload messages
    in `server/adapters/mcp/areas/scene.py`
- recorded the new Streamable HTTP regression coverage that separates:
  - scope-binding / spatial-refresh sequencing
  - clean failure of stale guided transform attempts
  - survival of the MCP session after those failures
- created `TASK-160` as the umbrella for the long-term solution, including:
  - the current baseline of what is already shipped
  - the failure taxonomy for client/harness vs repo runtime behavior
  - the option analysis for:
    - lightweight feedback on existing tool surfaces
    - a future structured `guided_flow_update`-style contract
    - optional FastMCP app-surface enhancement
    - client/harness behavior outside the repo boundary

## Validation

- `git diff --check`
- `poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py -k "describe_guided_flow_feedback_reports_spatial_refresh_requirements" -q`
  - result on this machine: `1 passed`
- `poetry run pytest tests/unit/tools/test_mcp_area_main_paths.py -k "async_modeling_transform or modeling_transform_object or async_modeling_create_emits_guided_flow_feedback" -q`
  - result on this machine: `7 passed`
- outside sandbox:
  - `poetry run pytest tests/e2e/integration/test_guided_streamable_spatial_support.py -k "view_diagnostics_requires_bound_scope_before_refresh_clears or transform_object_fails_cleanly_during_spatial_refresh_gate" -q -rs`
  - result on this machine: `2 passed`
