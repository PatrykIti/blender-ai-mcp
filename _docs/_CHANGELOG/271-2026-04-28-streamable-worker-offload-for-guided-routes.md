# 271. Streamable worker offload for guided routes

Date: 2026-04-28

## Summary

- kept blocking sync router/RPC execution off the FastMCP event loop when
  guided Streamable HTTP wrappers await post-route finalizers
- moved native async modeling create/transform routed execution through a
  worker thread before applying awaited guided dirty-state and role finalizers
- applied the same worker-thread route execution rule to the shared async route
  helper and async scene cleanup recovery path
- documented that awaited guided finalizers must not make Blender-backed sync
  handlers run on the Streamable HTTP event loop

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_context_bridge.py::test_async_guided_finalizer_wrapper_offloads_sync_tool_and_finalizes_report -q`
- `poetry run pytest tests/unit/adapters/mcp/test_context_bridge.py::test_route_tool_call_async_offloads_sync_route_report_execution -q`
- `poetry run pytest tests/unit/tools/test_mcp_area_main_paths.py::test_async_modeling_transform_finalizes_corrected_result_name_and_warning tests/unit/tools/test_mcp_area_main_paths.py::test_async_modeling_create_offloads_routed_sync_execution -q`
