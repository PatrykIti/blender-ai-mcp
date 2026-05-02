# TASK-158-04-02: Reference Understanding Session Linkage And Checkpoint Contracts

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-158-04](./TASK-158-04_Reference_Understanding_Internal_Contract_And_Guided_Handoff.md)
**Category:** Guided Runtime / Reference Understanding Session State
**Estimated Effort:** Small

## Objective

Persist bounded reference-understanding linkage in session state and thread
declared fields through the compare/iterate checkpoint contracts without
creating a second gate-intake path or violating the strict MCP payload shapes.

## Repository Touchpoints

| Path / Module | Expected Change |
|---------------|-----------------|
| `server/adapters/mcp/session_capabilities.py` | Add owning helpers or a `replace(...)`-based field for persisted reference-understanding linkage |
| `server/adapters/mcp/contracts/reference.py` | Add declared compare/iterate payload fields only if the linkage must become client-facing |
| `server/adapters/mcp/areas/reference.py` | Thread declared linkage fields through `_stage_compare_response(...)`, `_iterate_stage_response(...)`, and `_compact_compare_result_for_iterate(...)` |
| `server/adapters/mcp/contracts/quality_gates.py` | Reuse the live `TASK-157` intake/evidence-ref path instead of creating a second reference-specific normalizer |
| `tests/unit/adapters/mcp/test_quality_gate_intake.py` | Verify reference-derived proposals still normalize through the live intake seam |
| `tests/unit/adapters/mcp/test_guided_flow_state_contract.py` | Verify persisted session linkage is normalized and remains session-scoped |
| `tests/unit/adapters/mcp/test_reference_images.py` | Verify compare/iterate payloads and compact-iterate behavior stay aligned |
| `tests/unit/adapters/mcp/test_contract_payload_parity.py` | Keep strict contract parity for any new response fields |

## Implementation Notes

- Use the live `ingest_quality_gate_proposal[_async](...)` seam in
  `session_capabilities.py`; do not add a second reference-specific gate
  normalizer.
- If the client needs explicit linkage, persist:
  - `understanding_id`
  - a bounded public summary view
  - accepted gate ids or another explicitly declared linkage field
- `SessionCapabilityState` is frozen. Use an owning helper or `replace(...)`
  and `set_session_capability_state(...)`, not in-place mutation.
- `ReferenceCompareStageCheckpointResponseContract` and
  `ReferenceIterateStageCheckpointResponseContract` reject undeclared extras.
  Any public linkage field must be added explicitly and threaded through the
  compare/iterate helpers.
- Respect the current compact-iterate behavior. If nested `compare_result`
  linkage is trimmed for compact mode, document and test that policy instead of
  leaking stale undeclared fields.

## Pseudocode

```python
intake_result = ingest_quality_gate_proposal(
    ctx,
    gate_proposal.model_dump(mode="json", exclude_none=True),
)
accepted_gate_plan = intake_result.gate_plan if intake_result.status == "accepted" else None

state = get_session_capability_state(ctx)
state = replace(
    state,
    reference_understanding_summary={
        "understanding_id": summary_contract.understanding_id,
        "accepted_gate_ids": accepted_gate_ids,
        "summary": summary_contract.model_dump(mode="json", exclude_none=True),
    },
)
set_session_capability_state(ctx, state)
```

## Runtime / Security Contract Notes

- Visibility level: internal/session-scoped by default; public response fields
  require explicit declaration and tests.
- Read-only behavior: this slice must not mutate Blender scene state.
- Session/auth assumptions: linkage data is scoped to the active stdio or
  Streamable HTTP session and must not cross sessions implicitly.

## Tests To Add / Update

- Extend `tests/unit/adapters/mcp/test_quality_gate_intake.py` for
  reference-derived proposal normalization on the live intake seam.
- Extend `tests/unit/adapters/mcp/test_guided_flow_state_contract.py` for
  persisted linkage helpers and session normalization.
- Extend `tests/unit/adapters/mcp/test_reference_images.py` and
  `tests/unit/adapters/mcp/test_contract_payload_parity.py` for declared
  compare/iterate payload fields and compact-mode behavior.

## Docs To Update

- `_docs/_MCP_SERVER/README.md` if compare/iterate payloads change
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` if public linkage fields
  become normative

## Changelog Impact

- If this leaf closes independently, add a scoped `_docs/_CHANGELOG/*` entry in
  the same branch and update `_docs/_CHANGELOG/README.md`.
- If multiple `TASK-158` leaves land together in one wave, one shared
  completion entry may cover them, but it must name this leaf explicitly and
  record its validation in the summary.

## Status / Board Update

- This leaf stays under `TASK-158-04`; `_docs/_TASKS/README.md` remains on the
  umbrella row only.
- When this slice closes, record which session helper and checkpoint response
  fields changed so transport closeout can target the right lanes.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py -v`
- `rg -n "reference_understanding_summary|understanding_id|accepted_gate_ids|reference_understanding_gate_ids" server/adapters/mcp/session_capabilities.py server/adapters/mcp/areas/reference.py server/adapters/mcp/contracts/reference.py tests/unit/adapters/mcp`

## Acceptance Criteria

- Reference-derived proposals normalize through the live `TASK-157` intake seam.
- Session linkage stays bounded, session-scoped, and explicitly declared.
- Compare/iterate payloads remain strict and compact-mode-safe.
