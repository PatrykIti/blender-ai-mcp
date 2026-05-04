# TASK-145-01-03: Planner Summary Placement and Compare/Iterate Budget Gates

**Parent:** [TASK-145-01](./TASK-145-01_Repair_Planner_Payload_And_Family_Selection_Policy.md)
**Status:** ✅ Done
**Priority:** 🔴 High
**Depends On:** [TASK-145-01-01](./TASK-145-01-01_Planner_Envelope_And_Provenance_Contract.md), [TASK-145-01-02](./TASK-145-01-02_Deterministic_Family_Selection_From_Scope_Relation_And_View_Signals.md)

## Objective

Decide exactly where planner data lives in the staged reference loop so that:

- compare / iterate expose a compact planner summary
- richer planner detail is disclosed only when justified
- existing `budget_control` and trimming behavior stay authoritative

## Implementation Notes

- Compact compare / iterate responses may include a small planner summary, but
  must not embed full relation graphs, full truth bundles, or full candidate
  evidence by default.
- Rich/detail planner output must be derived from the same compare/iterate
  evidence and policy result. It must not require a new planner session or a
  second routing loop.
- `ReferenceHybridBudgetControlContract` remains the payload-size authority.
  Planner fields must participate in the same compact/rich budget rules.
- If planner-specific budget counters or trim reasons are needed, add explicit
  contract fields or a local builder/helper. Do not assume
  `ReferenceHybridBudgetControlContract` has mutating helper methods beyond the
  existing contract/model API.
- V1 should first use the existing `preset_profile="rich"` and compare/iterate
  response contracts for richer planner detail. A separate detail retrieval
  surface is allowed only if it reuses an explicit existing checkpoint/session
  artifact lifetime; do not add a new `planner_state` persistence model.
- If a separate detail retrieval surface is introduced later, it should be
  read-only, bounded, and backed by the current stage state.
- Any new planner-detail MCP surface must document the runtime/security
  contract required by `AGENTS.md`: visibility level, read-only behavior,
  stdio/Streamable HTTP/local RPC assumptions, parameter validation,
  reject-unknown behavior, payload limits, recovery behavior, and log/redaction
  expectations.
- `planner_summary`, `planner_detail`, and `planner_result` below describe the
  intended payload split. They do not exist in the current stage response until
  this leaf adds or maps them through the owning reference contracts.

## Pseudocode

```python
planner_summary = planner_result.to_compact_summary()
planner_detail = planner_result.to_detail() if include_detail else None
stage_budget_control = budget_control.model_copy(
    update={
        "detail_trimmed": budget_control.detail_trimmed or planner_result.detail_trimmed,
        "trimming_applied": budget_control.trimming_applied or planner_result.detail_trimmed,
    }
)

return _stage_compare_response(
    ...,
    refinement_route=planner_result.route,
    refinement_handoff=planner_result.handoff,
    planner_summary=planner_summary,
    planner_detail=planner_detail if preset_profile == "rich" else None,
    budget_control=stage_budget_control,
)
```

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/application/services/repair_planner.py` or equivalent policy helper
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`

## Acceptance Criteria

- planner summary placement is explicit in compare / iterate contracts
- default compare / iterate payload size does not regress into another heavy
  planner dump
- planner detail can expand in a goal-aware or handoff-aware way rather than
  staying fixed for every domain
- model-aware budget controls still trim scope/detail deterministically when
  needed
- any separate planner-detail surface is read-only, opt-in, visibility-gated,
  and covered by the explicit runtime/security contract checklist

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_PROMPTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`

## Validation Category

- Unit coverage must fail if compact mode reintroduces full heavy planner or
  debug payloads.
- Targeted command:
  `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_structured_contract_delivery.py tests/unit/adapters/mcp/test_guided_surface_benchmarks.py -q`

## Changelog Impact

- covered by the parent TASK-145 changelog entry:
  [_docs/_CHANGELOG/276-2026-04-30-task-145-repair-planner-handoff.md](../_CHANGELOG/276-2026-04-30-task-145-repair-planner-handoff.md)

## Completion Summary

Closed by wiring compact `planner_summary` into compare/iterate responses and
keeping `planner_detail` on the rich profile only. Compact iterate responses
preserve the actionable planner summary while omitting nested rich detail under
the existing budget-control path.

## Status / Board Update

- closed under TASK-145-01
