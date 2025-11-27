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

# Rules
1. **Prefix `collection_`**: All tools must start with this prefix.
2. **Read-Only**: Collection tools primarily query collection state; modification tools may be added in future phases.
3. **Deterministic Ordering**: Results are sorted alphabetically to prevent diff noise.
