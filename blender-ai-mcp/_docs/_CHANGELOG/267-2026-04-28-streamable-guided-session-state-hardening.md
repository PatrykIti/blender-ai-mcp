# 267. Streamable guided session-state hardening

Date: 2026-04-28

## Summary

- hardened guided state writes used by Streamable HTTP requests so registered
  scene/modeling tools await session-state and visibility updates instead of
  relying on sync wrappers that can detach work from the active JSON-RPC request
- kept the request-local session-state mirror populated after FastMCP
  serializable state writes so sync router-policy helpers can still see
  `guided_flow_state` during async tool execution
- added async registered variants for guided-state-mutating scene/modeling tools,
  including `scene_clean_scene`, spatial graph checks, view diagnostics,
  `modeling_create_primitive`, and `modeling_transform_object`
- added a shared deferred-finalizer wrapper for remaining dirty sync routed tools
  so mesh, scene, and modeling secondary mutators await guided spatial rearm on
  Streamable HTTP instead of doing sync post-route state writes inside the active
  request loop
- stopped sync guided-state updates from scheduling detached visibility-refresh
  tasks on an active FastMCP event loop; async transitions now await visibility
  refresh directly
- added `MCP_PROMPTS_AS_TOOLS_ENABLED` so prompt-capable clients can keep native
  MCP prompts without also exposing the `list_prompts` / `get_prompt` bridge
  tools
- disabled prompt bridge tools by default in `scripts/run_streamable_openrouter.sh`
  to reduce Claude Code context churn on Streamable HTTP guided sessions
- upgraded the task-runtime dependency line to FastMCP `3.2.4` with pydocket
  `0.19.x` and `pydantic-monty==0.0.11`
- documented when to leave the bridge enabled for tool-only clients and when to
  disable it for native prompt clients
- refreshed active MCP/prompt/runtime/test docs so the public guidance matches
  the 3.2.4/0.19.x runtime line and the optional prompt bridge

## Validation

- `poetry run pytest tests/unit -q`
- `poetry run pytest tests/unit/adapters/mcp/test_task_runtime_policy.py tests/unit/adapters/mcp/test_background_job_registry.py tests/unit/adapters/mcp/test_prompts_bridge.py tests/unit/adapters/mcp/test_server_factory.py tests/unit/adapters/mcp/test_code_mode_pilot.py tests/unit/adapters/mcp/test_scene_guided_scope_requirements.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py::test_spatial_check_completion_advances_flow_to_primary_masses tests/unit/adapters/mcp/test_guided_flow_state_contract.py::test_spatial_check_completion_reapplies_visibility tests/unit/tools/test_mcp_area_main_paths.py -q`
- `poetry run pytest tests/e2e/integration/test_guided_streamable_spatial_support.py -q -rs`
- `poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/adapters/mcp/test_code_mode_pilot_docs.py tests/unit/adapters/mcp/test_contract_docs.py tests/unit/adapters/mcp/test_platform_migration_docs.py tests/unit/adapters/mcp/test_sampling_assistant_docs.py tests/unit/adapters/mcp/test_elicitation_docs.py tests/unit/adapters/mcp/test_versioned_docs.py -q`
- `poetry run ruff check tests/e2e/integration/test_guided_streamable_spatial_support.py tests/unit/adapters/mcp/test_prompts_bridge.py server/infrastructure/config.py server/adapters/mcp/transforms/prompts_bridge.py server/adapters/mcp/factory.py server/adapters/mcp/server.py server/adapters/mcp/surfaces.py server/adapters/mcp/router_helper.py server/adapters/mcp/areas/_registration.py server/adapters/mcp/areas/scene.py server/adapters/mcp/areas/modeling.py server/adapters/mcp/areas/mesh.py server/adapters/mcp/session_capabilities.py server/adapters/mcp/session_state.py`
- `git diff --check`
