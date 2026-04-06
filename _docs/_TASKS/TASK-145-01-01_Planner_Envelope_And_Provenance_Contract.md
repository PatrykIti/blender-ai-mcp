# TASK-145-01-01: Planner Envelope and Provenance Contract

**Parent:** [TASK-145-01](./TASK-145-01_Repair_Planner_Payload_And_Family_Selection_Policy.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High  
**Depends On:** [TASK-122-03-07](./TASK-122-03-07_Deterministic_Cross_Domain_Refinement_Routing_And_Sculpt_Exposure.md), [TASK-143](./TASK-143_Guided_Spatial_Scope_And_Relation_Graphs.md), [TASK-144](./TASK-144_Camera_Aware_View_Graph_And_Visibility_Diagnostics.md)

## Objective

Define one bounded repair-planner contract that can sit above the current
`refinement_route` / `refinement_handoff` baseline and explicitly carry:

- family selection
- repair scope
- planner rationale / provenance
- blocker and precondition slots
- compact-vs-detail placement rules

The intended v1 posture is incremental:

- extend the current `refinement_route` / `refinement_handoff` contracts first
- only introduce a clearly separate planner contract family later if the
  existing route/handoff shape proves insufficient

## Repository Touchpoints

- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Acceptance Criteria

- the planner contract is machine-readable and bounded
- provenance stays separated by source class such as truth, macro, vision,
  scope, and view rather than being flattened into one fuzzy explanation
- the contract makes room for TASK-143 relation/scope outputs and TASK-144
  visibility outputs without embedding those full graphs by default
- inline compare / iterate responses can expose a compact planner derivative
  while richer planner detail remains opt-in or separately retrievable
- the first planner wave does not open an unnecessary second planner abstraction
  if the current route/handoff contracts can be evolved instead

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/LLM_GUIDE_V2.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Changelog Impact

- include in the parent TASK-145 changelog entry when shipped

## Status / Board Update

- no board change in this planning-only branch
