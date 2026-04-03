# TASK-122-03-07-02: Deterministic Refinement Family Selector

**Parent:** [TASK-122-03-07](./TASK-122-03-07_Deterministic_Cross_Domain_Refinement_Routing_And_Sculpt_Exposure.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

## Objective

Build a deterministic selector that turns hybrid-loop output into one bounded
refinement-family recommendation.

## Business Problem

The hybrid loop already knows a lot:

- truth findings
- ranked correction candidates
- vision shape/proportion drift
- target scope

But today it still does not answer a crucial operational question:

- should the next step stay in macro/modeling/mesh,
- or should it recommend a deterministic sculpt-family path?

## Technical Direction

Implement one selector that emits a bounded family result such as:

- `macro`
- `modeling_mesh`
- `sculpt_region`
- `inspect_only`

The selector must be:

- deterministic
- explainable from source signals
- bounded by allowlists, not open-ended prompt inference

The selector should use signals such as:

- presence/absence of high-priority macro candidates
- truth findings that are pairwise assembly issues
- vision evidence concentrated on local silhouette refinement with weak or no
  assembly failure
- scope shape:
  - single object
  - pair / object set
  - collection

It should also emit rationale that later docs/tests can validate.

## Repository Touchpoints

- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Acceptance Criteria

- selector emits one bounded refinement family from current loop signals
- selector keeps assembly cases on macro/modeling/mesh by default
- selector can choose `sculpt_region` for local organic/soft-form refinement
  cases without hard-coding one squirrel-only scenario

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped
