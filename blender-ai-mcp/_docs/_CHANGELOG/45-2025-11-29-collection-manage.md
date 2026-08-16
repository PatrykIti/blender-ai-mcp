# 45 - Collection Manage Tool (TASK-022)

**Date:** 2025-11-29
**Version:** 1.18.0

## Summary

Implemented `collection_manage` mega tool for comprehensive collection management in Blender. This tool enables AI to create, delete, rename, and organize collections as well as move/link/unlink objects between collections.

## Changes

### New MCP Tool

| Tool | Actions | Description |
|------|---------|-------------|
| `collection_manage` | create, delete, rename, move_object, link_object, unlink_object | Manages collections in the scene |

### Actions

- **create**: Create new collection (optionally under a parent collection)
- **delete**: Delete collection (objects moved to Scene Collection)
- **rename**: Rename collection
- **move_object**: Move object to collection (exclusive - unlinks from all others)
- **link_object**: Link object to collection (additive - keeps other links)
- **unlink_object**: Unlink object from collection

### Implementation

**4-Layer Architecture:**
1. **Domain** (`server/domain/tools/collection.py`): Added `manage_collection` abstract method
2. **Application** (`server/application/tool_handlers/collection_handler.py`): RPC bridge implementation
3. **Adapter** (`server/adapters/mcp/areas/collection.py`): MCP tool with semantic tags
4. **Addon** (`blender_addon/application/handlers/collection.py`): Full Blender API implementation

**RPC Registration:**
- `collection.manage` handler registered in `blender_addon/__init__.py`

### Testing

| Type | Count | Status |
|------|-------|--------|
| Unit tests | 21 | ✅ Pass |
| E2E tests | 7 | ✅ Ready |

### Files Changed

- `server/domain/tools/collection.py`
- `server/application/tool_handlers/collection_handler.py`
- `server/adapters/mcp/areas/collection.py`
- `blender_addon/application/handlers/collection.py`
- `blender_addon/__init__.py`
- `tests/unit/tools/collection/test_collection_manage.py` (new)
- `tests/e2e/tools/collection/test_collection_tools.py`

## Use Cases

- Organizing scene objects by type (lights, meshes, cameras)
- Creating asset hierarchies
- Managing visibility groups
- Preparing scenes for export (by collection)
