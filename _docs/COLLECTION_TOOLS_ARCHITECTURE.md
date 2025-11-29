# Collection Tools Architecture

Collection tools manage Blender collections (organizational containers for objects).
**Each operation is a separate tool** to ensure clarity and avoid context mixing.

---

# 1. collection_list ✅ Done
Lists all collections with hierarchy information, object counts, and visibility flags.

Args:
- include_objects: bool (default False) - if True, includes object names within each collection

Returns: List of collections with:
- name: str
- parent: str (parent collection name or "<root>")
- object_count: int
- child_count: int
- hide_viewport: bool
- hide_render: bool
- hide_select: bool
- objects: List[str] (if include_objects=True)

Example:
```json
{
  "tool": "collection_list",
  "args": {
    "include_objects": false
  }
}
```

---

# 2. collection_list_objects ✅ Done
Lists all objects within a specified collection (optionally recursive).

Args:
- collection_name: str - name of the collection to query
- recursive: bool (default True) - if True, includes objects from child collections
- include_hidden: bool (default False) - if True, includes hidden objects

Returns: Dict with:
- collection_name: str
- object_count: int
- recursive: bool
- include_hidden: bool
- objects: List of objects with name, type, visibility, selection state, location

Example:
```json
{
  "tool": "collection_list_objects",
  "args": {
    "collection_name": "MyCollection",
    "recursive": true,
    "include_hidden": false
  }
}
```

---

# 3. collection_manage ✅ Done
Comprehensive collection management: create, delete, rename, and move/link/unlink objects.

**Semantic Tags:** `[OBJECT MODE][SCENE][NON-DESTRUCTIVE]`

Args:
- action: str (required) - One of: "create", "delete", "rename", "move_object", "link_object", "unlink_object"
- collection_name: str (required) - Target collection name (or name to create)
- new_name: str (optional) - New name for rename action
- parent_name: str (optional) - Parent collection for create action (defaults to Scene Collection)
- object_name: str (optional) - Object name for move/link/unlink actions

### Actions

| Action | Required Args | Optional Args | Description |
|--------|---------------|---------------|-------------|
| `create` | `collection_name` | `parent_name` | Creates new collection (optionally under parent) |
| `delete` | `collection_name` | - | Deletes collection (objects moved to Scene Collection) |
| `rename` | `collection_name`, `new_name` | - | Renames collection |
| `move_object` | `collection_name`, `object_name` | - | Moves object to collection (exclusive - unlinks from all others) |
| `link_object` | `collection_name`, `object_name` | - | Links object to collection (additive - keeps other links) |
| `unlink_object` | `collection_name`, `object_name` | - | Unlinks object from collection |

### Examples

**Create collection:**
```json
{
  "tool": "collection_manage",
  "args": {
    "action": "create",
    "collection_name": "Lights",
    "parent_name": "Scene Elements"
  }
}
```

**Move object to collection:**
```json
{
  "tool": "collection_manage",
  "args": {
    "action": "move_object",
    "collection_name": "Characters",
    "object_name": "Player"
  }
}
```

**Link object to multiple collections:**
```json
{
  "tool": "collection_manage",
  "args": {
    "action": "link_object",
    "collection_name": "Export_Group",
    "object_name": "Player"
  }
}
```

---

# Rules
1. **Prefix `collection_`**: All tools must start with this prefix.
2. **Read-Only vs Write**: `collection_list` and `collection_list_objects` are read-only; `collection_manage` is write-capable.
3. **Deterministic Ordering**: Results are sorted alphabetically to prevent diff noise.
4. **Object Safety**: Deleting a collection moves objects to Scene Collection (not deleted).
