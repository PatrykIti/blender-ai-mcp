# 312. TASK-159 scene facade guards

Date: 2026-05-04

## Summary

- completed `TASK-159-02-01` by confirming the scene MCP public facade stayed
  stable while internal slices moved behind it
- kept in place:
  - `SCENE_PUBLIC_TOOL_NAMES`
  - `register_scene_tools(...)`
  - `_register_existing_tool(...)`
  - shared `version_policy.py` ownership of versioned scene surfaces
- validated that provider inventory ordering, surface manifest, versioned
  exposure, and public docstrings still match the current `scene.py` facade

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_provider_inventory.py tests/unit/adapters/mcp/test_provider_versions.py tests/unit/adapters/mcp/test_version_policy.py tests/unit/adapters/mcp/test_surface_manifest.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
  - result on this machine: `44 passed`
