# TASK-145-02-01: Sculpt Handoff Contract and Local Target Semantics

**Parent:** [TASK-145-02](./TASK-145-02_Sculpt_Handoff_Context_And_Precondition_Model.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Depends On:** [TASK-145-01-01](./TASK-145-01-01_Planner_Envelope_And_Provenance_Contract.md)

## Objective

Define a sculpt handoff contract that makes explicit:

- selected family
- target object / local scope
- region or local-form reason
- bounded recommended tools and argument hints

instead of relying on the current minimal `object_name`-only handoff shape.

## Repository Touchpoints

- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/sculpt.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`

## Acceptance Criteria

- the sculpt handoff clearly identifies the object or narrow local target that
  sculpt would act on
- the handoff includes an explicit local-form or region reason
- recommended tools remain bounded to the deterministic sculpt-region subset
- argument hints remain compatible with actual sculpt tool shapes in
  `server/adapters/mcp/areas/sculpt.py`

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`

## Changelog Impact

- include in the parent TASK-145 changelog entry when shipped

## Status / Board Update

- no board change in this planning-only branch
