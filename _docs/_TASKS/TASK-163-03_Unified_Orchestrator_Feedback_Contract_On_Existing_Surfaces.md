# TASK-163-03: Unified Orchestrator Feedback Contract On Existing Surfaces

**Status:** ✅ Done
**Priority:** 🔴 High
**Parent:** [TASK-163](./TASK-163_Vision_Orchestrator_Feedback_Strategy_Normalization_And_Optional_Perception_Adapters.md)
**Objective:** Expose one compact `reference_orchestrator_feedback` read model on existing reference/router/checkpoint surfaces.
**Repository Touchpoints:** `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/contracts/router.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_images_runtime.py`, `server/adapters/mcp/areas/router.py`
**Acceptance Criteria:** no new public flow; attach/remove/clear/list plus `router_*` and staged compare/iterate can all return the compact feedback contract.

## Completion Summary

- added typed `ReferenceOrchestratorFeedbackContract`
- projected it through `reference_images(...)`, `router_set_goal(...)`,
  `router_get_status(...)`, `reference_compare_stage_checkpoint(...)`, and
  `reference_iterate_stage_checkpoint(...)`
- kept richer stage payloads (`planner_summary`, `truth_followup`,
  `correction_candidates`) intact and treated the new contract as a compact
  read model instead of a replacement

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/vision/test_reference_understanding_runtime_surface.py`

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_TASKS/README.md`

## Changelog Impact

- covered by [318. TASK-163 reference orchestrator feedback core](../_CHANGELOG/318-2026-05-05-task-163-reference-orchestrator-feedback-core.md)

## Status / Board Update

- tracked under the open `TASK-163` umbrella
- does not become its own board row

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/router/application/test_router_contracts.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -k "reference_orchestrator_feedback_transport_surface or reference_understanding_transport_roundtrip or reference_understanding_refresh_replaces_gate_slice" -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_understanding_runtime_surface.py -k "reference_orchestrator_feedback_surface_with_real_blender_capture" -q`
