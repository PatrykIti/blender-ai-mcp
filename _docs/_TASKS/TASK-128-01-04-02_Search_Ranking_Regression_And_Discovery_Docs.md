# TASK-128-01-04-02: Search Ranking Regression and Discovery Docs

**Parent:** [TASK-128-01-04](./TASK-128-01-04_Creature_Blockout_Metadata_Search_Hints_And_Regression_Pack.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Add focused ranking regressions and public discovery docs so creature-oriented
search phrases keep surfacing the intended blockout tools.

## Repository Touchpoints

- `server/adapters/mcp/discovery/search_documents.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Acceptance Criteria

- regression coverage protects the intended search/discovery bias
- public docs explain the improved discovery path for creature blockout work
- the discovery layer remains metadata-driven

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_search_surface.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
