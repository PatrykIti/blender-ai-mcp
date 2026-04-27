# TASK-145-01-03: Planner Summary Placement and Compare/Iterate Budget Gates

**Parent:** [TASK-145-01](./TASK-145-01_Repair_Planner_Payload_And_Family_Selection_Policy.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Depends On:** [TASK-145-01-01](./TASK-145-01-01_Planner_Envelope_And_Provenance_Contract.md), [TASK-145-01-02](./TASK-145-01-02_Deterministic_Family_Selection_From_Scope_Relation_And_View_Signals.md)

## Objective

Decide exactly where planner data lives in the staged reference loop so that:

- compare / iterate expose a compact planner summary
- richer planner detail is disclosed only when justified
- existing `budget_control` and trimming behavior stay authoritative

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
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

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_PROMPTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`

## Changelog Impact

- include in the parent TASK-145 changelog entry when shipped

## Status / Board Update

- no board change in this planning-only branch
