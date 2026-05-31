# TASK-173-04: Existing Squirrel Proof-Lane Extension And Runtime Evidence Surfacing

**Parent:** [TASK-173](./TASK-173_Reference_Guided_Creature_Scope_Convergence_And_Optional_Grounding_Followups.md)
**Status:** ✅ Done
**Priority:** 🔴 High
**Follow-on After:** [TASK-171-06](./TASK-171-06_Squirrel_Regression_Proof_Docs_And_Closeout.md), [TASK-169-05](./TASK-169-05_Squirrel_Reference_Guided_Drift_Regression_Pack.md)
**Related:** [TASK-172-06](./TASK-172-06_Harness_Negative_Coverage_And_Operator_Docs_For_Optional_Vision_Runtime.md)
**Objective:** Extend the existing Blender-backed squirrel proof lane and add enough runtime-evidence surfacing that operators, harness runs, and status surfaces can tell which optional sidecars were configured, invoked, skipped, or unavailable during a guided creature session.
**Repository Touchpoints:** `scripts/vision_harness.py`, `tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/vision/test_reference_understanding_runtime_surface.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/unit/adapters/mcp/test_public_surface_docs.py`, `tests/unit/router/application/test_router_contracts.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/areas/router.py`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/session_capabilities_state.py`, `_docs/_VISION/README.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_TESTS/README.md`, `_docs/_TEST_IMAGES/squirrel-front.png`, `_docs/_TEST_IMAGES/squirrel-side.png`
**Acceptance Criteria:**
- the existing squirrel proof lane is extended rather than duplicated and still covers the front/side reference class end to end
- runtime artifacts or structured feedback make it visible whether classifier, vision, localization, and segmentation were actually used
- failure analysis for future regressions no longer requires manual docker-log archaeology to answer “which sidecars participated?”

## Implementation Notes

- the current investigation required manual correlation across:
  - thread/session outputs
  - docker logs
  - `/tmp/blender-ai-mcp` capture artifacts
  - reference images
- the repo already has the base squirrel proof lane from `TASK-169-05-02`;
  this task must extend that lane with runtime-evidence expectations instead of
  reopening the original “create the lane” deliverable
- the repo already has generic harness/docs work for optional vision under
  `TASK-172-06`; this task is the squirrel-specific extension on top of that
  surface, not a new generic harness family
- if the evidence needs to remain visible after compare/iterate returns, the
  task must also own the session-state seam that lets `router_get_status(...)`
  answer which optional runtimes actually participated
- the product needs a first-class diagnostic surface for this class of failure:
  - sidecars healthy but not necessarily activated
  - compare scope narrowing incorrectly
  - primitive blockout accepted too far into the loop
- surface only bounded evidence:
  - capability considered
  - capability invoked
  - capability skipped due to policy
  - capability unavailable
  - packet ids / checkpoint labels / target scope that drove that decision

## Pseudocode

```python
session_evidence = {
    "classifier": capability_usage_summary(classifier_runtime),
    "vision": capability_usage_summary(vision_runtime),
    "localization": capability_usage_summary(localization_runtime),
    "segmentation": capability_usage_summary(segmentation_runtime),
    "packets": packet_scope_and_activation_summary(compare_run),
}
attach_runtime_evidence(reference_orchestrator_feedback, session_evidence)
```

## Runtime / Security Contract Notes

- runtime evidence must stay bounded and redact secrets/provider-key material
- avoid dumping raw provider payloads into public feedback
- harness/debug output should be sufficient for diagnosis without turning logs
  into the primary product surface

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py`
- `tests/e2e/vision/test_reference_understanding_runtime_surface.py`
- targeted harness assertions in `scripts/vision_harness.py`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- board tracking is closed on umbrella `TASK-173`
- no separate promoted board-row change is expected for this subtask unless it
  later becomes a standalone follow-on

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/router/application/test_router_contracts.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py tests/e2e/vision/test_reference_understanding_runtime_surface.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`

## Validation Category

- regression proof and runtime-evidence observability

## Completion Summary

Completed on 2026-05-31. Compare, iterate, feedback, router status, and the
localized-support harness now expose bounded `runtime_evidence` for classifier,
main vision, localization, and segmentation participation. The existing
squirrel proof lane was extended with runtime-evidence assertions instead of
duplicating the lane, so future failures can tell whether optional sidecars
were configured, considered, invoked, skipped by policy, unavailable, or absent
without log archaeology.

Validation evidence is recorded in changelog entry `394`.
