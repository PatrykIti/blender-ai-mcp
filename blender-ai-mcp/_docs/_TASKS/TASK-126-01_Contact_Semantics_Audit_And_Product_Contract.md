# TASK-126-01: Contact Semantics Audit and Product Contract

**Parent:** [TASK-126](./TASK-126_Mesh_Aware_Contact_Semantics_And_Visual_Fit_Reliability.md)  
**Status:** ✅ Done
**Priority:** 🔴 High

**Completion Summary:** The product contract is now explicit across the public
surface: `scene_measure_gap(...)`, `scene_measure_overlap(...)`, and
`scene_assert_contact(...)` describe mesh-surface truth as the preferred path
for mesh pairs and bbox semantics as a fallback. Router tool metadata and
top-level docs were aligned to stop overclaiming bbox contact as proof of
visual fit.

## Objective

Define one explicit product contract for:

- bbox-touching
- mesh/surface contact
- visible gap / visible overlap

instead of letting those meanings blur together in the current truth layer.

## Business Problem

Today the repo can effectively say "contact passed" when what it really proved
is only that two axis-aligned bounding boxes touch.

That wording/contract drift is confusing for:

- operators
- macro follow-up logic
- hybrid correction loops
- docs and prompts

## Technical Direction

Audit the current first-wave scene truth tools and write down:

- what they actually measure today
- which fields/warnings/messages overclaim visual truth
- which product surfaces need a stronger semantic split

Then define one explicit product contract for the next implementation leaves.

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/application/tool_handlers/macro_handler.py`
- `server/adapters/mcp/areas/reference.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- the repo has one explicit contract for bbox-touching vs true mesh/surface
  contact
- operator-facing wording no longer overclaims what bbox-based checks prove
- later implementation leaves have a clear target behavior to build against

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`

## Tests To Add/Update

- docs/contract coverage as needed

## Changelog Impact

- include in the parent task changelog entry when shipped
