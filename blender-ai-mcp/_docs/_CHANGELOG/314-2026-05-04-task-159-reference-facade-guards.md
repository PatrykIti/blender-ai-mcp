# 314. TASK-159 reference facade guards

Date: 2026-05-04

## Summary

- completed `TASK-159-01-01` by confirming the reference public facade stayed
  stable while internal bounded side branches moved behind it
- kept in place:
  - `REFERENCE_PUBLIC_TOOL_NAMES`
  - `register_reference_tools(...)`
  - the provider/manifest-facing registration seam in `reference.py`
  - the public checkpoint/stage wrapper names and discovery surface
- validated provider inventory, tool inventory, surface manifest, and public
  docs against the current reference facade state after the refactor wave

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_provider_inventory.py tests/unit/adapters/mcp/test_tool_inventory.py tests/unit/adapters/mcp/test_surface_manifest.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
  - result on this machine: `42 passed`
