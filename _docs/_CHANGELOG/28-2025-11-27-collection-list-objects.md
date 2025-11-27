# Changelog: Collection List Objects Tool (TASK-014-7)

## Added
- Extended collection domain/application interfaces with `list_objects` method.
- MCP tool `collection_list_objects` listing objects within specified collection with recursive and hidden object filtering.
- Blender addon implementation:
  - Validates collection existence via `bpy.data.collections.get`
  - Supports recursion using stack (processes child collections)
  - Filters hidden objects based on `hide_viewport`/`hide_render`
  - Returns deterministic sorted output avoiding duplicates
- RPC endpoint `collection.list_objects` registered in `blender_addon/__init__.py`.

## Documentation
- Updated TASK-014-7 status to Done, task board statistics.
- Added `collection_list_objects` to COLLECTION_TOOLS_ARCHITECTURE.md and available tools summary.

## Testing
- Manual testing recommended: nested collections, hidden objects filter, invalid collection name error handling.

## Version
1.9.7
