# TASK-128-01-04: Creature Blockout Metadata, Search Hints, and Regression Pack

**Parent:** [TASK-128-01](./TASK-128-01_Guided_Creature_Prompting_Handoff_And_Discovery_Hints.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Strengthen discovery/search bias and public docs so creature-oriented phrases
rank the right modeling tools without forcing the model into broad unguided
search loops.

## Current Runtime Baseline

Search-first discovery already exists on `llm-guided`. This slice is about
metadata quality and ranking regressions, not about rebuilding BM25/search
plumbing.

## Current Drift To Resolve

Current audited runtime behavior still over-ranks generic organic/noise tools
for creature blockout phrasing. The task delta is to make creature blockout
search practical, not merely available.

Current concrete failure shape:

- build-phase creature queries such as
  `low poly creature ears snout tail arc paw placement organic blockout`
  still return rankings like:
  - `macro_adjust_segment_chain_arc`
  - `mesh_randomize`
  - `mesh_create_vertex_group`
  - `macro_place_symmetry_pair`
  - `mesh_smooth`
  - `mesh_assign_to_group`
  - `mesh_remove_from_group`
  - `mesh_set_proportional_edit`
- that means the current search-first surface is technically available but
  still operationally misleading for low-poly creature blockout

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

Current negative group to beat in regressions includes:

- `mesh_randomize`
- `mesh_smooth`
- `mesh_create_vertex_group`
- `mesh_assign_to_group`
- `mesh_remove_from_group`
- similar broad-shape or grouping/administrative helpers that are not first
  blockout actions

Technical clarification:

- this slice is not about replacing BM25/search plumbing or adding a special
  hardcoded creature search mode
- it is about fixing the shaped search inputs that the existing discovery layer
  indexes:
  - metadata vocabulary in `tools_metadata/**`
  - how `search_documents.py` merges metadata, aliases, keywords, sample
    prompts, and related tools
- regressions should protect positive ranking for core blockout tools and
  negative ranking against generic “organic noise” tools such as
  `mesh_randomize`, `mesh_smooth`, and similar broad-shape helpers when the
  query clearly expresses creature blockout intent

## Repository Touchpoints

- `server/router/infrastructure/tools_metadata/modeling/modeling_create_primitive.json`
- `server/router/infrastructure/tools_metadata/modeling/modeling_transform_object.json`
- `server/router/infrastructure/tools_metadata/mesh/mesh_extrude_region.json`
- `server/router/infrastructure/tools_metadata/mesh/mesh_loop_cut.json`
- `server/router/infrastructure/tools_metadata/mesh/mesh_bevel.json`
- `server/router/infrastructure/tools_metadata/mesh/mesh_symmetrize.json`
- `server/router/infrastructure/tools_metadata/mesh/mesh_merge_by_distance.json`
- `server/router/infrastructure/tools_metadata/mesh/mesh_dissolve.json`
- `server/router/infrastructure/tools_metadata/mesh/mesh_create_vertex_group.json`
- `server/router/infrastructure/tools_metadata/mesh/mesh_assign_to_group.json`
- `server/router/infrastructure/tools_metadata/mesh/mesh_remove_from_group.json`
- `server/router/infrastructure/tools_metadata/scene/macro_adjust_relative_proportion.json`
- `server/router/infrastructure/tools_metadata/scene/macro_adjust_segment_chain_arc.json`
- `server/adapters/mcp/discovery/search_documents.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- creature-oriented search phrases rank relevant blockout tools materially
  better than today
- the task defines explicit sentinel queries that must stop returning
  generic/noise tools ahead of core blockout tools
- metadata stays generic and reusable beyond squirrels
- docs/regressions lock the new discovery bias in place
- focused regressions prove that creature blockout queries prefer blockout tools
  over generic organic surface tools and current vertex-group false positives
- the technical seam is explicit: metadata/search-document enrichment drives
  the ranking change; the task must not be satisfiable by docs-only wording

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py` when discovery
  payload/footprint expectations need to acknowledge the new creature-bias
  regressions

## Changelog Impact

- include in the parent slice changelog entry when shipped

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-128-01-04-01](./TASK-128-01-04-01_Creature_Metadata_Taxonomy_And_Tool_Target_List.md) | Define the exact metadata vocabulary and first target tool list for creature blockout |
| 2 | [TASK-128-01-04-02](./TASK-128-01-04-02_Search_Ranking_Regression_And_Discovery_Docs.md) | Lock the discovery bias with ranking regressions and public docs |
