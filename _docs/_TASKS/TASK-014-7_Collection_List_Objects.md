# TASK-014-7: Collection List Objects Tool

**Status:** ⏳ To Do  
**Priority:** 🟢 Low  
**Phase:** Phase 7 - Introspection & Listing APIs

## 🎯 Objective
Expose a tool that returns all objects contained within a specified collection (optionally recursive), including basic metadata for each entry.

## 🏗️ Architecture Requirements
### 1. Domain Layer (`server/domain/tools/collection_list_objects.py`)
- Define request model with `collection_name: str`, `recursive: bool = True`, `include_hidden: bool = False`.
- Response model containing collection summary plus array of `CollectionObjectSummary` (name, type, visibility, selection state).
- Interface `ICollectionListObjectsTool.list_objects(request) -> CollectionObjectsReport`.

### 2. Application Layer (`server/application/handlers/collection_list_objects_handler.py`)
- Handler delegates to RPC `collection.list_objects` and handles `CollectionNotFoundError` cleanly.

### 3. Adapter Layer
- Register MCP tool `collection_list_objects(name: str, recursive: bool = True, include_hidden: bool = False) -> str`.
- Docstring: `[COLLECTION][SAFE][READ-ONLY] Lists objects inside collection; optionally dives into child collections.`

### 4. Blender Addon API (`blender_addon/api/collection_list_objects_api.py`)
- Validate collection existence via `bpy.data.collections.get`.
- Support recursion using stack, optionally filtering hidden objects (check `obj.hide_viewport`/`obj.hide_render`).

### 5. RPC Server & Addon Registration
- Register `collection.list_objects` endpoint.
- **IMPORTANT:** Register handler in `blender_addon/__init__.py`:
  ```python
  rpc_server.register_handler("collection.list_objects", collection_handler.list_objects)
  ```

## ✅ Deliverables
- Domain contracts + models.
- Handler + DI wiring.
- Adapter tool entry.
- Blender API + RPC registration.
- Docs/changelog + README update.

## 🧪 Testing
- Collections with nested children.
- Hidden objects filter.
- Invalid collection name -> descriptive error.

## 📚 References
- `_docs/TOOLS_ARCHITECTURE_DEEP_DIVE.md` clean architecture guidance.
