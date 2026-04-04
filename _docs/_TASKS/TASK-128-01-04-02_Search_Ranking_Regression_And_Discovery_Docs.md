# TASK-128-01-04-02: Search Ranking Regression and Discovery Docs

**Parent:** [TASK-128-01-04](./TASK-128-01-04_Creature_Blockout_Metadata_Search_Hints_And_Regression_Pack.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Add focused ranking regressions and public discovery docs so creature-oriented
search phrases keep surfacing the intended blockout tools.

## Current Drift To Resolve

The current runtime can still rank tools like `mesh_randomize` and
`mesh_smooth` above creature blockout actions for broad creature queries. This
leaf should lock that failure mode out with explicit regressions.

The canonical failure query from the audit is:

- `low poly creature ears snout tail arc paw placement organic blockout`

This leaf should also cover adjacent natural queries such as:

- `animal head ears snout silhouette side reference`
- `snout shape extrude loop cut low poly animal head`
- `tail arc proportion creature body silhouette`

## Repository Touchpoints

- `server/adapters/mcp/discovery/search_documents.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Acceptance Criteria

- regression coverage protects the intended search/discovery bias for both
  creature blockout queries and staged reference-loop queries
- regressions define explicit “must rank in / must not outrank” expectations for
  the core blockout group versus generic noise/smoothing groups
- public docs explain the improved discovery path for creature blockout work
- the discovery layer remains metadata-driven
- regressions verify that creature blockout queries prefer core blockout tools
  over generic organic-noise tools
- the regression pack is scoped to the shaped public story:
  build-phase guided discovery should help the model find blockout tools early,
  not just prove that every relevant tool is technically searchable somewhere

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py` if payload-size
  or shaped-surface benchmark notes need to mention the new creature-bias
  discovery expectations

## Changelog Impact

- include in the parent slice changelog entry when shipped
