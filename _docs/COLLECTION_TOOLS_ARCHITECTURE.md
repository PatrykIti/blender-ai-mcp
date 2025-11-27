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

# Rules
1. **Prefix `collection_`**: All tools must start with this prefix.
2. **Read-Only**: Collection tools primarily query collection state; modification tools may be added in future phases.
3. **Deterministic Ordering**: Results are sorted alphabetically to prevent diff noise.
