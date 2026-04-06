# TASK-143-01-02: Public Scene Surface and Router Metadata for Scope Graph

**Parent:** [TASK-143-01](./TASK-143-01_Scope_Graph_Contract_And_Read_Only_Surface.md)
**Depends On:** [TASK-143-01-01](./TASK-143-01-01_Scope_Artifact_Role_Vocabulary_And_Shared_Builder.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Expose the scope graph through a dedicated read-only scene tool/module and make
it router/search aware without turning it into a default bootstrap-visible
guided tool.

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/dispatcher.py`
- `server/infrastructure/di.py`
- `server/router/infrastructure/tools_metadata/scene/`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Acceptance Criteria

- the repo has one explicit read-only scene-facing scope artifact surface
- router metadata exists for the new scope artifact and links it sensibly to
  existing scene truth tools
- the new surface can be executed through the normal internal tool-routing path
  where required
- the tool remains discoverable/searchable without becoming automatically
  bootstrap-visible on `llm-guided`
- this slice does not enlarge stage compare / iterate payloads just to make the
  scope artifact reachable

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Changelog Impact

- include in the parent `TASK-143` changelog entry when shipped

## Status / Board Update

- keep board tracking on `TASK-143`
- no `_docs/_TASKS/README.md` change in this planning pass
