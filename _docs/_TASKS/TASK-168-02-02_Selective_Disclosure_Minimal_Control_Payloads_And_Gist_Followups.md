# TASK-168-02-02: Selective Disclosure, Minimal Control Payloads, And Additive Detail Followups

**Status:** ✅ Done
**Priority:** 🔴 High
**Parent:** [TASK-168-02](./TASK-168-02_Typed_Orchestrator_Feedback_Contract_And_Emission_Points.md)
**Objective:** Make compact compare/iterate outputs truly compact for external controllers while preserving the current additive top-level public shape and keeping heavy packet/truth detail out of the default compact path.
**Repository Touchpoints:** `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_planner.py`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/contracts/router.py`, `server/adapters/mcp/areas/reference_feedback.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/e2e/integration/test_guided_surface_contract_parity.py`, `tests/e2e/vision/test_reference_understanding_runtime_surface.py`
**Acceptance Criteria:**
- compact mode keeps the existing top-level surface additive and returns a
  controller-sized payload anchored on `reference_orchestrator_feedback`,
  `compare_diagnostics`, and other existing public fields first
- heavy packet/truth/planner detail is omitted from the default compact path unless:
  - uncertainty
  - error
  - hard failure
  - explicit rich mode via `preset_profile="rich"`
- compare/iterate can carry one short bounded summary of unresolved packet
  state between iterations by reusing existing additive fields such as
  `correction_focus`, `evidence_summary`, and `uncertainty_notes` instead of
  replaying the whole detail blob
- external controllers can keep driving the current workstep without reading a giant txt/json dump

## Implementation Notes

- keep the public surface additive and top-level; do not invent a wrapper such
  as `control` / `summary` / `detail` around the shipped compare/iterate
  payload
- compact mode should keep `reference_orchestrator_feedback` as the control
  owner seam and `compare_diagnostics` as the public uncertainty path while
  omitting heavy nested compare/truth/planner detail unless rich mode,
  uncertainty, error, or hard-failure handling requires it
- bounded carry-forward state should reuse existing additive fields such as:
  - `correction_focus`
  - `evidence_summary`
  - `uncertainty_notes`
- if a richer detail-followup path is still needed later, it must land as an
  additive extension on the current public surface rather than a parallel
  wrapper or summary handle
- this task should make `compact` mean "controller-sized," not just "smaller
  than rich"

## Pseudocode

```python
payload = {
    "reference_orchestrator_feedback": build_reference_orchestrator_feedback(...),
    "compare_diagnostics": build_compare_diagnostics(...),
}

if preset_profile == "rich" or uncertainty or hard_failure:
    payload["compare_result"] = build_compare_detail_payload(...)

return payload
```

## Runtime / Security Contract Notes

- compact payload must not depend on the client parsing human prose
- heavy detail should remain bounded and redacted
- any carry-forward summary must not become stale hidden state; it should be
  recomputed from the authoritative compare/runtime result each iteration

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/vision/test_reference_understanding_runtime_surface.py`

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- historical closeout entry ownership belongs to
  [TASK-168-04](./TASK-168-04_Profile_Contract_Rewrite_Validation_And_Closeout.md)

## Status / Board Update

- closed administratively under the completed `TASK-168-02` and `TASK-168`
  parents on 2026-05-16
- the final family proof is recorded in
  [TASK-168-04](./TASK-168-04_Profile_Contract_Rewrite_Validation_And_Closeout.md)
  and
  [355. TASK-168 guided registry final drift repair](../_CHANGELOG/355-2026-05-16-task-168-guided-registry-final-drift-repair.md)

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- focused Blender-backed owner lanes to cover under the repo-supported runner:
  - `tests/e2e/integration/test_guided_surface_contract_parity.py`
  - `tests/e2e/vision/test_reference_understanding_runtime_surface.py`
- `poetry run python scripts/run_e2e_tests.py`

## Validation Category

- compact-output contract tests plus repo-supported Blender E2E proof
- `git diff --check`
