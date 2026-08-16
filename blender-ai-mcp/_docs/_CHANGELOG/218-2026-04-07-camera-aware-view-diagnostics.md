# 218. Camera-aware view diagnostics

Date: 2026-04-07

## Summary

Completed TASK-144 by shipping one explicit read-only view-space diagnostics
layer: public `scene_view_diagnostics(...)`, Blender-backed projection and
occlusion/framing runtime support, bounded guided disclosure, and compact
reference-loop recommendation hints instead of a heavyweight embedded view
graph.

## What Changed

- added one typed scene diagnostics contract family for:
  - requested/resolved view-source provenance
  - projected center and coarse 2D extent
  - frame coverage and centering
  - visible/partial/occluded/off-frame verdicts
- added `scene_view_diagnostics(...)` to the public scene MCP area
- added Blender addon/runtime support for:
  - named-camera diagnostics
  - mirrored `USER_PERSPECTIVE` diagnostics
  - bounded focus/orbit/standard-view reuse
  - best-effort occlusion sampling plus reversible view-state restore
- wired the new surface through:
  - scene domain/application handler APIs
  - addon RPC registration
  - dispatcher mapping
  - router metadata
  - provider/discovery inventory
- kept `llm-guided` bootstrap unchanged while exposing the new tool on
  build/inspect and guided-handoff paths
- updated `reference_compare_current_view(...)` to emit compact
  `view_diagnostics_hints` when framing or occlusion ambiguity makes the
  current checkpoint a weak basis for the next correction step
- updated README/docs/prompt guidance, task files/board state, and regression
  coverage for the shipped view-space layer

## Validation

- ran targeted unit coverage for the new scene contracts, addon/runtime path,
  MCP surface wiring, search/visibility shaping, structured delivery, guided
  benchmarks, and reference-loop hints:
  - `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/scene/test_viewport_control.py tests/unit/tools/test_handler_rpc_alignment.py tests/unit/adapters/mcp/test_structured_contract_delivery.py tests/unit/adapters/mcp/test_provider_inventory.py tests/unit/adapters/mcp/test_tool_inventory.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_guided_surface_benchmarks.py tests/unit/adapters/mcp/test_reference_images.py -q`
- result: `189 passed`
- added Blender-backed E2E coverage for `scene_view_diagnostics(...)`, but did
  not run the E2E suite in this branch

## Why

The guided stack already had strong truth artifacts and strong image capture,
but it still lacked one explicit answer to “what is actually visible from this
view right now?”. Shipping a separate view-space layer lets the model reason
about framing and occlusion with typed facts while preserving the repo’s
guiding constraint: small guided bootstrap surfaces and bounded default
compare/iterate payloads.
