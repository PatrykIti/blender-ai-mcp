# 273. Async rename validation offload

Date: 2026-04-29

## Summary

- moved async guided part-registry rename validation through a worker thread so
  `require_existing_scene_object_name(...)` does not run Blender-backed
  `scene.list_objects()` on the Streamable HTTP event loop
- kept the sync guided rename path unchanged for ordinary synchronous tool
  wrappers
- added regression coverage for the async rename finalizer to verify validation
  is offloaded before the guided part registry is updated
- refreshed MCP docs to include async identity finalizers in the Streamable HTTP
  event-loop safety contract

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py::test_async_guided_rename_validation_runs_off_event_loop -q`
- `poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py -q`
