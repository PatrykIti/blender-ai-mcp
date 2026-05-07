# TASK-137-03: Organ Regression, Docs, And Medical Guardrail Closeout

**Status:** ⏳ To Do
**Priority:** 🟠 High
**Parent:** [TASK-137](./TASK-137_Anatomy_Aware_Reference_Guided_Organ_Reconstruction.md)
**Depends On:** [TASK-137-01](./TASK-137-01_Organ_Domain_Boundary_Vocabulary_And_Fidelity_Tiers.md), [TASK-137-02](./TASK-137-02_Guided_Organ_Loop_Relation_Semantics_And_Bounded_Surface.md), [TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md), [TASK-158](./TASK-158_Vision_And_Creature_Gate_Boundary_Doc_Alignment.md), [TASK-163](./TASK-163_Vision_Orchestrator_Feedback_Strategy_Normalization_And_Optional_Perception_Adapters.md)
**Objective:** Lock the first organ domain slice with regression, docs, and explicit proof that the product boundary stays non-clinical.
**Repository Touchpoints:** `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_images_runtime.py`, `server/adapters/mcp/areas/reference_truth.py`, `server/adapters/mcp/areas/router.py`, `server/adapters/mcp/transforms/quality_gate_verifier.py`, `server/application/services/spatial_graph.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/unit/adapters/mcp/test_public_surface_docs.py`, `tests/unit/adapters/mcp/test_quality_gate_verifier.py`, `tests/unit/tools/scene/test_scene_contracts.py`, `tests/unit/tools/scene/test_spatial_graph_service.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/vision/test_reference_understanding_runtime_surface.py`, future `tests/e2e/vision/test_guided_organ_reconstruction.py`, `_docs/_PROMPTS/README.md`, likely new `_docs/_PROMPTS/REFERENCE_GUIDED_ORGAN_BUILD.md`, `_docs/_VISION/README.md`, `_docs/_MCP_SERVER/README.md`, `_docs/AVAILABLE_TOOLS_SUMMARY.md`, `_docs/_TESTS/README.md`, `_docs/_TASKS/README.md`, `_docs/_CHANGELOG/`
**Acceptance Criteria:** the first organ E2E lane proves staged organ blockers on the live transport surface; docs and changelog state explicit non-clinical limits; operator guidance does not overclaim what the domain can do.

## Implementation Notes

- keep the first regression pack small and focused on one or two bounded organ
  scenarios
- include explicit negative checks for overclaiming, such as diagnosis or
  patient-specific interpretation language
- document the domain boundary only after the runtime surface actually enforces
  it
- keep closeout proof on the existing `reference_images(...)`,
  `router_get_status(...)`, `reference_compare_stage_checkpoint(...)`, and
  `reference_iterate_stage_checkpoint(...)` surfaces instead of treating a
  docs-only audit as sufficient
- before closing this leaf, rerun the earlier unit owner lanes from
  `TASK-137-01` / `TASK-137-02` and then the repo-standard full unit pass so
  the closeout is not transport-only

## Pseudocode

```python
run_unit_owner_lanes_for_organ_contract()
run_transport_lane_for_staged_gate_reporting()
run_first_bounded_organ_e2e_lane()
audit_docs_for_non_clinical_boundary_consistency()
```

## Runtime / Security Contract Notes

- do not close this slice without explicit docs/runtime alignment on the
  non-clinical boundary
- proof should use the existing transport/runtime seams, not docs-only review
- once the first dedicated organ E2E lane exists, final runtime closeout should
  use the repo-supported Blender runner `poetry run python scripts/run_e2e_tests.py`
  instead of treating one ad hoc pytest invocation as sufficient

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_quality_gate_verifier.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/scene/test_spatial_graph_service.py`
- future `tests/e2e/vision/test_guided_organ_reconstruction.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/vision/test_reference_understanding_runtime_surface.py`

## Docs To Update

- `_docs/_PROMPTS/README.md`
- likely new `_docs/_PROMPTS/REFERENCE_GUIDED_ORGAN_BUILD.md`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the first organ regression/docs
  closeout ships.
- Use explicit `TASK-137` wording in the changelog title/body instead of
  referring to the family only as `137`, because `_docs/_CHANGELOG/137-*`
  already belongs to unrelated historical work.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/scene/test_spatial_graph_service.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit -q`
- `poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `poetry run pytest tests/e2e/vision/test_reference_understanding_runtime_surface.py -q`
- `poetry run python scripts/run_e2e_tests.py`

## Status / Board Update

- keep `_docs/_TASKS/README.md` on the umbrella `TASK-137` row until the parent
  umbrella actually closes
- when `TASK-137` closes, update the umbrella, this leaf, and any sibling
  leaves in the same branch so no open direct child remains under a closed
  parent
