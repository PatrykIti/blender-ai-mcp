# TASK-166-01: View And Scope Packet Compare Family

**Parent:** [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Define one deterministic packet family for compare/iterate that decomposes work by view and active scope instead of sending one full-scene compare payload.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference_planner.py`
- `server/application/services/`
- `server/adapters/mcp/vision/capture_runtime.py`
- `server/adapters/mcp/vision/capture.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/integration/`

## Implementation Notes

- Introduce an internal compare-plan result that can emit:
  - `view_packets`
  - `scope_packets`
  - `packet_order`
  - `synthesis_required`
- Keep the compare-plan builder out of the `@mcp.tool` body once it becomes
  more than simple data selection; `reference_compare_stage_checkpoint(...)`
  should call a dedicated helper/service and remain the staged-response
  assembler.
- Packet planning must support:
  - front-only runs
  - front+side runs
  - optional top/silhouette packets
  - active-scope packets such as `Body + Head`, `Tail`, `Ears`

## Current Flow Integration

- Keep `reference_compare_stage_checkpoint(...)` and
  `reference_iterate_stage_checkpoint(...)` as the public entrypoints.
- Insert packet planning and packet-local capture/reference narrowing
  immediately before the current `build_vision_request_from_stage_captures(...)`
  path.
- Keep the plan aligned with the live staged capture seam in
  `server/adapters/mcp/vision/capture_runtime.py`; packet planning is not only
  about request assembly after captures already exist.
- Packet planning also has to align with the pre-request truth/framing seams in
  `server/adapters/mcp/areas/reference_truth.py` and
  `server/adapters/mcp/areas/reference_view_diagnostics.py`, because staged
  compare currently resolves truth bundle and framing hints before final request
  assembly.
- Reuse current `target_view`, `target_object`, `target_objects`, and
  `collection_name` as packet-planning hints rather than treating them as the
  final whole-request scope.
- Reuse current reference selection and stage capture seams as the first
  narrowing layer, but allow the packet plan to further slice the selected
  captures/reference ids per packet so one packet wrapper does not still ship a
  monolithic request underneath.

## Pseudocode

```text
compare_plan = build_compare_plan(
  stage=current_guided_step,
  gate_plan=active_gate_plan,
  assembled_scope=assembled_target_scope,
  reference_records=selected_reference_records,
  target_view=target_view,
)
packet_inputs = select_packet_inputs(
  compare_plan=compare_plan,
  captures=stage_captures,
  reference_records=selected_reference_records,
)
```

## Runtime / Security Contract Notes

- Packet boundaries stay server-owned and deterministic.
- Public compare contracts may expose packet diagnostics, but not hidden
  internal-only packet planning state that leaks irrelevant scene details.

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- one `_docs/_CHANGELOG/` entry when packet planning ships

## Status / Board Update

- keep `TASK-166` as the promoted board row
- update this subtask, relevant leaves, and the board summary in
  `_docs/_TASKS/README.md` together when packet planning closes or splits

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`

## Acceptance Criteria

- compare/iterate no longer assumes one monolithic request shape
- packet planning is deterministic and stage-aware
- each packet can identify its packet-local view/scope, selected reference ids,
  and selected capture labels without inventing a second public flow
