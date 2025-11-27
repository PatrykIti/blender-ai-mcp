# Changelog: Collection List Tool (TASK-014-6)

## Added
- New domain layer `server/domain/tools/collection.py` with `ICollectionTool` interface.
- Collection handler implementations:
  - `blender_addon/application/handlers/collection.py` - CollectionHandler traversing bpy.data.collections
  - `server/application/tool_handlers/collection_handler.py` - CollectionToolHandler for RPC
- MCP tool `collection_list` listing collections with hierarchy (parent/child counts), object counts, visibility flags.
- Optional `include_objects` parameter to list object names per collection.
- DI provider `get_collection_handler()` in `server/infrastructure/di.py`.
- RPC endpoint `collection.list` registered in `blender_addon/__init__.py`.

## Documentation
- Updated TASK-014-6 status to Done, task board statistics.
- Created new section "Collection Tools" in MCP server adapter.
- Added collection_list to available tools summary.
- Will create COLLECTION_TOOLS_ARCHITECTURE.md in next update.

## Testing
- Manual testing recommended: scenes with nested collections, verify hierarchy output and visibility flags.

## Version
1.9.6
