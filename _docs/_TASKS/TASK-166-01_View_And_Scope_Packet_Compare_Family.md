# TASK-166-01: View And Scope Packet Compare Family

**Parent:** [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Define one deterministic packet family for compare/iterate that decomposes work by view and active scope instead of sending one full-scene compare payload.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/reference_checkpoint_compare.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference_planner.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/integration/`

## Implementation Notes

- Introduce an internal compare-plan result that can emit:
  - `view_packets`
  - `scope_packets`
  - `packet_order`
  - `synthesis_required`
- Packet planning must support:
  - front-only runs
  - front+side runs
  - optional top/silhouette packets
  - active-scope packets such as `Body + Head`, `Tail`, `Ears`

## Current Flow Integration

- Keep `reference_compare_stage_checkpoint(...)` and
  `reference_iterate_stage_checkpoint(...)` as the public entrypoints.
- Insert packet planning immediately before the current
  `build_vision_request_from_stage_captures(...)` path.
- Reuse current `target_view`, `target_object`, `target_objects`, and
  `collection_name` as packet-planning hints rather than treating them as the
  final whole-request scope.

## Pseudocode

```text
compare_plan = build_compare_plan(
  stage=current_guided_step,
  assembled_scope=assembled_target_scope,
  reference_records=selected_reference_records,
  target_view=target_view,
)
```

## Runtime / Security Contract Notes

- Packet boundaries stay server-owned and deterministic.
- Public compare contracts may expose packet diagnostics, but not hidden
  internal-only packet planning state that leaks irrelevant scene details.

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- one `_docs/_CHANGELOG/` entry when packet planning ships

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`

## Acceptance Criteria

- compare/iterate no longer assumes one monolithic request shape
- packet planning is deterministic and stage-aware
