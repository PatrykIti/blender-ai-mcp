# TASK-022: Collection Management Tools

**Status:** To Do
**Priority:** 🟡 Medium
**Category:** Collection Tools

---

## Overview

Implement collection management tools for organizing objects in Blender's outliner hierarchy.

---

# TASK-022-1: collection_manage

**Status:** To Do
**Priority:** 🟡 Medium

## Objective

Implement `collection_manage` mega tool for creating, deleting, renaming, and moving collections.

## Architecture Requirements

### 1. Domain Layer (`server/domain/tools/collection.py`)

Extend `ICollectionTool` interface:

```python
@abstractmethod
def manage_collection(
    self,
    action: str,  # 'create', 'delete', 'rename', 'move_object', 'link_object', 'unlink_object'
    collection_name: str,
    new_name: str = None,  # for 'rename'
    parent_name: str = None,  # for 'create' - parent collection
    object_name: str = None,  # for 'move_object', 'link_object', 'unlink_object'
) -> str:
    pass
```

### 2. Application Layer (`server/application/tool_handlers/collection_handler.py`)

Implement RPC bridge in `CollectionToolHandler`.

### 3. Adapter Layer (`server/adapters/mcp/areas/collection.py`)

```python
@mcp.tool()
def collection_manage(
    ctx: Context,
    action: Literal["create", "delete", "rename", "move_object", "link_object", "unlink_object"],
    collection_name: str,
    new_name: str = None,
    parent_name: str = None,
    object_name: str = None,
) -> str:
    """
    [OBJECT MODE][SCENE][NON-DESTRUCTIVE] Manages collections in the scene.

    Actions:
        - create: Create new collection (optionally under parent)
        - delete: Delete collection (objects moved to scene root)
        - rename: Rename collection
        - move_object: Move object to collection (unlinks from others)
        - link_object: Link object to collection (keeps other links)
        - unlink_object: Unlink object from collection

    Workflow: BEFORE -> collection_list | AFTER -> collection_list_objects

    Args:
        action: Operation to perform
        collection_name: Target collection name
        new_name: New name (for 'rename' action)
        parent_name: Parent collection (for 'create' action)
        object_name: Object to move/link/unlink
    """
```

### 4. Blender Addon (`blender_addon/application/handlers/collection.py`)

Extend `CollectionHandler`:

```python
def manage_collection(self, action, collection_name, new_name=None, parent_name=None, object_name=None):
    if action == "create":
        new_col = bpy.data.collections.new(collection_name)
        parent = bpy.data.collections.get(parent_name) if parent_name else bpy.context.scene.collection
        parent.children.link(new_col)
        return f"Created collection '{collection_name}'"

    elif action == "delete":
        col = bpy.data.collections.get(collection_name)
        if not col:
            return f"Collection '{collection_name}' not found"
        bpy.data.collections.remove(col)
        return f"Deleted collection '{collection_name}'"

    elif action == "rename":
        col = bpy.data.collections.get(collection_name)
        if not col:
            return f"Collection '{collection_name}' not found"
        col.name = new_name
        return f"Renamed '{collection_name}' to '{new_name}'"

    elif action == "move_object":
        # Unlink from all, link to target
        obj = bpy.data.objects.get(object_name)
        col = bpy.data.collections.get(collection_name)
        for c in obj.users_collection:
            c.objects.unlink(obj)
        col.objects.link(obj)
        return f"Moved '{object_name}' to '{collection_name}'"

    elif action == "link_object":
        obj = bpy.data.objects.get(object_name)
        col = bpy.data.collections.get(collection_name)
        col.objects.link(obj)
        return f"Linked '{object_name}' to '{collection_name}'"

    elif action == "unlink_object":
        obj = bpy.data.objects.get(object_name)
        col = bpy.data.collections.get(collection_name)
        col.objects.unlink(obj)
        return f"Unlinked '{object_name}' from '{collection_name}'"
```

### 5. Registration

Register RPC handler in `blender_addon/__init__.py`.

## Deliverables

- [ ] Domain interface extension
- [ ] Application handler implementation
- [ ] MCP adapter with docstrings
- [ ] Blender addon handler
- [ ] Unit tests
- [ ] Documentation updates

## Use Cases

- Organizing scene objects by type (lights, meshes, cameras)
- Creating asset hierarchies
- Managing visibility groups
- Preparing scenes for export (by collection)
