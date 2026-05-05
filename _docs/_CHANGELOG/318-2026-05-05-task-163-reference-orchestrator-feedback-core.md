# 318. TASK-163 reference orchestrator feedback core

Implemented the first `TASK-163` delivery wave on the existing
reference/router/checkpoint seams.

## What Changed

- expanded `ReferenceUnderstandingSummaryContract` with typed `views` and
  server-owned `visual_metrics`
- added session-scoped `reference_strategy_state` so normalized
  `construction_path` / family policy survives guided session persistence
- added compact `reference_orchestrator_feedback` on:
  - `reference_images(...)`
  - `router_set_goal(...)`
  - `router_get_status(...)`
  - `reference_compare_stage_checkpoint(...)`
  - `reference_iterate_stage_checkpoint(...)`
- added deterministic lightweight RU image metrics:
  - `edge_density`
  - `contour_count`
  - `polygonal_contour_ratio`
  - `dominant_color_count`
  - `silhouette_aspect_ratio`
  - `facet_likelihood`
- kept the richer compare/iterate payloads unchanged as the deeper proof/debug
  surface; the new feedback contract is a compact read model, not a replacement
- created the physical `TASK-163*` docs family and promoted the umbrella on the
  board

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_parsing.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/router/application/test_router_contracts.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -k "reference_understanding_transport_roundtrip or reference_understanding_refresh_replaces_gate_slice" -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -k "reference_orchestrator_feedback_transport_surface or reference_understanding_transport_roundtrip or reference_understanding_refresh_replaces_gate_slice" -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_understanding_runtime_surface.py -k "reference_orchestrator_feedback_surface_with_real_blender_capture" -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit -q`
- `poetry run python scripts/run_e2e_tests.py`
