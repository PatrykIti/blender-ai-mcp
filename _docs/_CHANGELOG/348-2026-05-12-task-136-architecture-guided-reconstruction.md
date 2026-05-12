# 348. TASK-136 architecture guided reconstruction

Date: 2026-05-12

Task: `TASK-136`, `TASK-136-01`, `TASK-136-02`, `TASK-136-03`

## Summary

Closed the first reference-guided architecture reconstruction slice on the
existing building, guided-flow, quality-gate, staged-compare, and spatial-truth
surfaces. The new path gives plan/elevation/facade reference goals an explicit
architecture prompt and guided handoff without adding a parallel compare,
workflow, or verifier system.

## Changes

- Added `reference_guided_architecture_build` to native prompt discovery,
  prompt recommendations, prompt bridge exposure, guided-flow prompt bundles,
  and guided handoff contracts.
- Extended the building guided role sequence to require `footprint_mass`,
  `main_volume`, and `wall_shell` before secondary `facade_opening`,
  `opening_grid`, `support_element`, `roof_mass`, and `detail_element` work.
- Expanded building quality-gate templates with wall shell, roof/wall seam,
  facade-opening, facade-rhythm, and optional support-contact gates.
- Added `opening_wall` attachment semantics and strengthened architecture
  relation truth across `spatial_graph.py` and staged `reference_truth.py`.
- Added architecture packet labels such as `Facade + Openings`, `Roofline`,
  and `Supports` on the existing staged compare packet path.
- Shaped router no-match behavior, visibility, and search so plan/elevation
  /facade/reference architecture goals stay on the bounded guided building
  surface instead of silently importing `simple_house_workflow`.
- Updated README, prompt, MCP, router, vision, tests, task-board, and
  changelog docs for the shipped architecture path.

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_quality_gate_contracts.py tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py tests/unit/adapters/mcp/test_prompt_catalog.py tests/unit/adapters/mcp/test_prompt_provider.py tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py tests/unit/adapters/mcp/test_prompts_bridge.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/router/application/test_router_handler_parameters.py tests/unit/tools/scene/test_spatial_graph_service.py tests/unit/adapters/mcp/test_reference_compare_packets.py -q` (`183 passed`)
- `poetry run pytest ./tests/unit` (`3382 passed`)
- `poetry run python scripts/run_e2e_tests.py` (`476 passed, 3 skipped`; log: `tests/e2e/e2e_test_PASSED_20260513_011104.log`)
