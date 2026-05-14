# TASK-168-02-02: Selective Disclosure, Minimal Control Payloads, And Gist Followups

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-168-02](./TASK-168-02_Typed_Orchestrator_Feedback_Contract_And_Emission_Points.md)
**Objective:** Make compact compare/iterate outputs truly compact for external controllers by separating a tiny control payload from heavy packet/truth detail and by carrying only short gist/state between iterations.
**Repository Touchpoints:** `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_planner.py`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/contracts/router.py`, `server/adapters/mcp/areas/reference_feedback.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/e2e/integration/test_guided_surface_contract_parity.py`, `tests/e2e/vision/test_reference_understanding_runtime_surface.py`
**Acceptance Criteria:**
- compact mode returns one small controller-facing payload first
- heavy packet/truth/planner detail is omitted from the default controller path unless:
  - uncertainty
  - hard failure
  - explicit rich mode
  - explicit follow-up detail request
- compare/iterate can carry one short gist / summary of unresolved packet state between iterations instead of replaying the whole detail blob
- external controllers can keep driving the current workstep without reading a giant txt/json dump

## Implementation Notes

- keep existing public contracts when possible, but split fields conceptually:
  - `control`
  - `detail`
- likely compact-control fields:
  - `active_scope`
  - `correction_focus`
  - `top_blockers`
  - `best_next_action`
  - `do_now`
  - `dont_do`
  - `wont_work`
  - `next_compare_args`
- likely detail-on-demand fields:
  - packet diagnostics
  - expanded truth bundle
  - full planner detail
  - expanded evidence refs
- gist carry-forward should summarize:
  - which packet/scope is unresolved
  - what changed since the last checkpoint
  - whether escalation is required
- this task should make `compact` mean “controller-sized,” not just “smaller than rich”

## Pseudocode

```python
if preset_profile == "compact" and not uncertainty and not explicit_detail:
    return {
        "control": build_compact_control_payload(...),
        "gist": build_checkpoint_gist(...),
    }

return {
    "control": build_compact_control_payload(...),
    "gist": build_checkpoint_gist(...),
    "detail": build_compare_detail_payload(...),
}
```

## Runtime / Security Contract Notes

- compact payload must not depend on the client parsing human prose
- heavy detail should remain bounded and redacted
- gist must not become stale hidden state; it should be recomputed from the
  authoritative compare/runtime result each iteration

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
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

- remains nested under `TASK-168-02`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_understanding_runtime_surface.py -q`

## Validation Category

- compact-output contract tests
- `git diff --check`
