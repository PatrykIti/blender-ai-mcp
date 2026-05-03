# TASK-159-01-02: Reference Truth, Planner, And Service Promotion Split

**Parent:** [TASK-159-01](./TASK-159-01_Reference_Area_Modularization_And_Checkpoint_Assembly_Boundaries.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Extract truth-bundle and repair-planner helper clusters from `reference.py`,
and promote any framework-free logic into `server/application/services/` when it
no longer needs MCP-only imports.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- likely new helper modules such as:
  - `server/adapters/mcp/areas/reference_truth.py`
  - `server/adapters/mcp/areas/reference_planner.py`
- `server/application/services/`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/contracts/scene.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `tests/e2e/vision/test_goal_derived_gate_support_symmetry_surfaces.py`

## Current Code Anchors

- `_build_correction_truth_bundle(...)`
- `_truth_bundle_pairs(...)`
- `_build_refinement_handoff(...)`
- `_build_repair_planner_summary(...)`
- `_build_repair_planner_detail(...)`
- `_support_tools_from_blockers(...)`

## Planned Code Shape

```python
from .reference_truth import build_correction_truth_bundle
from .reference_planner import build_refinement_handoff

truth_bundle = build_correction_truth_bundle(...)
planner = build_refinement_handoff(...)
```

## Runtime / Security Contract Notes

- keep deterministic truth authoritative over planner/perception summaries
- preserve typed follow-up items, macro candidates, and blocker summaries
- if logic moves into `server/application/services/`, keep MCP contract shaping
  in the adapter layer

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `tests/e2e/vision/test_goal_derived_gate_support_symmetry_surfaces.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py tests/e2e/vision/test_reference_stage_truth_handoff.py tests/e2e/vision/test_goal_derived_gate_support_symmetry_surfaces.py -q`

## Docs To Update

- inherit parent docs closeout unless service promotion changes documented
  ownership in `ARCHITECTURE.md`

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- truth/planner helper clusters have explicit homes outside the monolith
- staged compare/iterate contracts still expose the same typed truth and planner
  payloads
- any promoted service logic is framework-free and does not drag FastMCP imports
  into the application layer

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
