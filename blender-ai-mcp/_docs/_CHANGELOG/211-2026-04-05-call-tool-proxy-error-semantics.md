# 211. call_tool proxy error semantics

Date: 2026-04-05

## Summary

Hardened the guided discovery `call_tool(...)` proxy so proxied tool failures
preserve the same error semantics as direct tool calls.

## What Changed

- removed the `ValueError` catch in the discovery `call_tool(...)` proxy that
  previously converted proxied tool failures into normal text results
- proxied validation/runtime failures now propagate as real tool errors, so
  clients can detect failure reliably instead of continuing on a false success
  path
- added focused regression coverage proving that a proxied `ValueError`
  remains an error instead of becoming a successful `ToolResult`
- updated MCP surface docs to state that guided `call_tool(...)` preserves the
  same failure semantics as direct tool execution

## Why

Discovery is only safe if the execution proxy behaves like the tool it is
calling. Flattening proxied errors into success text weakens failure handling
and can let clients continue a workflow with invalid assumptions.

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_search_surface.py -q`
