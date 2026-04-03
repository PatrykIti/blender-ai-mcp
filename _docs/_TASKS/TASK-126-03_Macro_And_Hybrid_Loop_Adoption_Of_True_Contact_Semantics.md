# TASK-126-03: Macro and Hybrid Loop Adoption of True Contact Semantics

**Parent:** [TASK-126](./TASK-126_Mesh_Aware_Contact_Semantics_And_Visual_Fit_Reliability.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

## Objective

Update macro verification and hybrid truth-bundle consumers so they stop
treating bbox-touching as sufficient proof of visually correct fit.

## Business Problem

Even if the scene truth layer gets a better contact model, the product still
fails if downstream consumers keep using the old semantics to declare success.

Current high-risk surfaces include:

- macro verification reports
- `truth_followup`
- `correction_candidates`
- staged compare/iterate decisions

## Technical Direction

Update downstream consumers so:

- macro reports use the right contact semantics for "fixed" vs "still needs
  work"
- hybrid truth bundles and correction loops do not prematurely stop on
  rounded/curved visual-gap cases
- operator-facing guidance reflects the new truth split

## Repository Touchpoints

- `server/application/tool_handlers/macro_handler.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `tests/unit/tools/macro/`
- `tests/unit/adapters/mcp/`
- `tests/e2e/vision/`

## Acceptance Criteria

- macro verification does not claim visual-fit success too early on curved-gap
  cases
- hybrid correction payloads reflect the more truthful contact semantics
- staged loops no longer close out obviously gapped assemblies as fixed just
  because bbox contact passed

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_PROMPTS/README.md` if operator guidance changes

## Tests To Add/Update

- `tests/unit/tools/macro/`
- `tests/unit/adapters/mcp/`
- `tests/e2e/vision/`

## Changelog Impact

- include in the parent task changelog entry when shipped
