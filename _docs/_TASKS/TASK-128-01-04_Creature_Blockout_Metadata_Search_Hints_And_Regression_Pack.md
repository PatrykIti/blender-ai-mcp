# TASK-128-01-04: Creature Blockout Metadata, Search Hints, and Regression Pack

**Parent:** [TASK-128-01](./TASK-128-01_Guided_Creature_Prompting_Handoff_And_Discovery_Hints.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Strengthen discovery/search bias and public docs so creature-oriented phrases
rank the right modeling tools without forcing the model into broad unguided
search loops.

## Technical Direction

Enrich blockout-tool metadata for phrases such as:

- `animal head`
- `ears`
- `snout`
- `muzzle`
- `tail arc`
- `paw placement`
- `silhouette`
- `front reference`
- `side reference`
- `low poly creature`
- `organic blockout`

Start with the core blockout tools most likely to matter during creature work:

- `modeling_create_primitive`
- `modeling_transform_object`
- `mesh_extrude_region`
- `mesh_loop_cut`
- `mesh_bevel`
- `mesh_symmetrize`
- `mesh_merge_by_distance`
- `mesh_dissolve`
- `macro_adjust_relative_proportion`
- `macro_adjust_segment_chain_arc`

## Repository Touchpoints

- `server/router/infrastructure/tools_metadata/modeling/modeling_create_primitive.json`
- `server/router/infrastructure/tools_metadata/modeling/modeling_transform_object.json`
- `server/router/infrastructure/tools_metadata/mesh/mesh_extrude_region.json`
- `server/router/infrastructure/tools_metadata/mesh/mesh_loop_cut.json`
- `server/router/infrastructure/tools_metadata/mesh/mesh_bevel.json`
- `server/router/infrastructure/tools_metadata/mesh/mesh_symmetrize.json`
- `server/router/infrastructure/tools_metadata/mesh/mesh_merge_by_distance.json`
- `server/router/infrastructure/tools_metadata/mesh/mesh_dissolve.json`
- `server/router/infrastructure/tools_metadata/scene/macro_adjust_relative_proportion.json`
- `server/router/infrastructure/tools_metadata/scene/macro_adjust_segment_chain_arc.json`
- `server/adapters/mcp/discovery/search_documents.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- creature-oriented search phrases rank relevant blockout tools materially
  better than today
- metadata stays generic and reusable beyond squirrels
- docs/regressions lock the new discovery bias in place

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_search_surface.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-128-01-04-01](./TASK-128-01-04-01_Creature_Metadata_Taxonomy_And_Tool_Target_List.md) | Define the exact metadata vocabulary and first target tool list for creature blockout |
| 2 | [TASK-128-01-04-02](./TASK-128-01-04-02_Search_Ranking_Regression_And_Discovery_Docs.md) | Lock the discovery bias with ranking regressions and public docs |
