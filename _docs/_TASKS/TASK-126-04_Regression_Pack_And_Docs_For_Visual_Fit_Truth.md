# TASK-126-04: Regression Pack and Docs for Visual Fit Truth

**Parent:** [TASK-126](./TASK-126_Mesh_Aware_Contact_Semantics_And_Visual_Fit_Reliability.md)  
**Status:** ⏳ To Do  
**Priority:** 🟡 Medium

## Objective

Protect the new contact semantics with focused regression coverage and docs so
the repo does not slide back into bbox-only "looks fixed" claims.

## Business Problem

This class of bug is easy to reintroduce because:

- numbers can look correct while the viewport still looks wrong
- docs may over-summarize contact as "touching"
- macro/hybrid tests can miss visibly gapped rounded forms

## Technical Direction

Add regression scenarios that explicitly cover:

- rounded head/body and face-feature gaps
- bbox-touching vs visually gapped cases
- hybrid-loop and macro outputs after those cases

Update docs so operators know what the truth layer does and does not prove.

## Repository Touchpoints

- `tests/unit/tools/scene/`
- `tests/unit/tools/macro/`
- `tests/unit/adapters/mcp/`
- `tests/e2e/tools/scene/`
- `tests/e2e/vision/`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_TASKS/README.md`

## Acceptance Criteria

- regression coverage includes visibly gapped curved/rounded cases
- docs explicitly describe the updated truth semantics
- future changes can be judged against realistic viewport-visible failures, not
  only bbox math

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`

## Tests To Add/Update

- focused unit and E2E regression coverage for visual-fit truth semantics

## Changelog Impact

- include in the parent task changelog entry when shipped
