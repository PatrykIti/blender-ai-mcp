# TASK-014-6: Collection List Tool

**Status:** ✅ Done
**Priority:** 🟢 Low
**Phase:** Phase 7 - Introspection & Listing APIs
**Completion Date:** 2025-11-27

## 🎯 Objective
Implement a tool that lists all collections with hierarchy depth, object counts, and visibility flags, enabling AI agents to reason about scene organization.

## 🏗️ Architecture Requirements
### 1. Domain Layer (`server/domain/tools/collection_list.py`)
- Define response model containing collection name, parent, child_count, object_count, visibility states (viewport/render/selectable).
- Interface `ICollectionListTool.list_collections() -> List[CollectionSummary]`.

### 2. Application Layer (`server/application/handlers/collection_list_handler.py`)
- Handler calls RPC `collection.list` and formats response text tree (indentation based on depth).

### 3. Adapter Layer
- Add MCP tool `collection_list(ctx: Context) -> str` with docstring `[COLLECTION][SAFE][READ-ONLY] Lists all collections and hierarchy info.`
- Provide optional `include_objects: bool = False` argument to toggle listing object names per collection.

### 4. Blender Addon API (`blender_addon/api/collection_list_api.py`)
- Traverse `bpy.data.collections`, compute tree recursively, respect optional `include_objects` flag.
- Return deterministic ordering (e.g., alphabetical) to prevent diff noise.

### 5. RPC Registration & Addon Registration
- Register endpoint `collection.list`.
- **IMPORTANT:** Register handler in `blender_addon/__init__.py`:
  ```python
  # Collection
  collection_handler = CollectionHandler()
  rpc_server.register_handler("collection.list", collection_handler.list_collections)
  ```

## ✅ Deliverables
- Domain interface/model.
- Handler + DI setup.
- Adapter tool with docstring + parameter validation.
- Addon API logic + RPC hook.
- Update docs/changelog + README Phase 7.

## 🧪 Testing
- Scenes with nested collections to confirm depth output.
- Hidden collections -> verify visibility flags.

## 📚 References
- `_docs/TOOLS_ARCHITECTURE_DEEP_DIVE.md`
- `README` Phase 7 item "collection_list".
