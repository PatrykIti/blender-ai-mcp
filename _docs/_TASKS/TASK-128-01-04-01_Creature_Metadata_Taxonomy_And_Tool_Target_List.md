# TASK-128-01-04-01: Creature Metadata Taxonomy and Tool Target List

**Parent:** [TASK-128-01-04](./TASK-128-01-04_Creature_Blockout_Metadata_Search_Hints_And_Regression_Pack.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Define the exact creature/blockout metadata vocabulary and the first batch of
tool metadata files to update.

## Current Drift To Resolve

The current target metadata files still mostly speak in generic modeling terms,
so this leaf must define the creature/blockout vocabulary before ranking
regressions can be meaningful.

The metadata plan also needs to say what it is explicitly trying to beat.
Right now broad tokens still make tools like `mesh_randomize` or
`mesh_smooth` look competitive for creature blockout queries, and current live
queries can also pull in vertex-group tools such as `mesh_create_vertex_group`,
`mesh_assign_to_group`, or `mesh_remove_from_group`, even when the intent is
clearly “build the main masses / features,” not “add organic noise” or “manage
selection groups.”

## Repository Touchpoints

- `server/router/infrastructure/tools_metadata/modeling/`
- `server/router/infrastructure/tools_metadata/mesh/`
- `server/router/infrastructure/tools_metadata/scene/`
- `server/adapters/mcp/discovery/search_documents.py`
- `tests/unit/adapters/mcp/test_search_surface.py`

## Acceptance Criteria

- the task defines a reusable generic creature vocabulary
- the first target tool list is explicit and bounded
- the metadata plan stays reusable beyond squirrel-specific examples
- the initial vocabulary covers creature-blockout phrases such as ears, snout,
  muzzle, tail arc, paw placement, silhouette, front reference, side
  reference, low-poly creature, and organic blockout
- the vocabulary/target list also identifies which generic broad-shape terms
  and which grouping/administrative tool families should **not** dominate
  creature blockout ranking without stronger matching evidence
- the output is concrete enough that ranking regressions can assert against
  specific positive and negative tool groups rather than vague “better search”

## Changelog Impact

- include in the parent slice changelog entry when shipped
