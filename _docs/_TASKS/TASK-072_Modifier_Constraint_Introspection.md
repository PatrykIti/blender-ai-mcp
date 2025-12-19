# TASK-072: Modifier & Constraint Introspection

**Priority:** 🔴 High  
**Category:** Scene/Modeling Introspection  
**Estimated Effort:** Medium  
**Dependencies:** TASK-014-14 (Scene Inspect Modifiers)  
**Status:** ⏳ TODO

---

## 🎯 Objective

Expose full modifier parameters and object constraints for 1:1 reconstruction and rig validation.

---

## ✅ Naming Conventions (Introspection Tools)

- `get_*` = raw data payload (full modifier/constraint data)
- `list_*` = names or lightweight summaries only
- `inspect_*` = aggregated stats (human-readable)
- `analyze_*` = heuristics/interpretation (not raw data)
- Parameters: `object_name`, `modifier_name`, `include_bones`

---

## 🔧 Sub-Tasks

### TASK-072-1: modeling_get_modifier_data

**Status:** ⏳ TODO

```python
@mcp.tool()
def modeling_get_modifier_data(
    ctx: Context,
    object_name: str,
    modifier_name: str | None = None,
    include_node_tree: bool = False
) -> str:
    """
    [OBJECT MODE][READ-ONLY][SAFE] Returns full modifier properties.
    """
```

**Return JSON (example):**
```json
{
  "object_name": "Body",
  "modifiers": [
    {
      "name": "Bevel",
      "type": "BEVEL",
      "properties": {"width": 0.002, "segments": 3},
      "object_refs": []
    }
  ]
}
```

**Notes:**
- `include_node_tree=true` should include Geometry Nodes *group metadata only*:
  - `node_tree.name`
  - `node_tree.is_linked` + `node_tree.library_path` (if linked)
  - `inputs[]`: `name`, `identifier`, `socket_type`, `default_value`, `min`, `max`, `subtype`
  - `outputs[]`: `name`, `identifier`, `socket_type`
- Do NOT include internal nodes, links, or geometry data.
- Keep payload stable and deterministic (sorted by input index).

**Geometry Nodes JSON (example):**
```json
{
  "object_name": "Body",
  "modifiers": [
    {
      "name": "GeometryNodes",
      "type": "NODES",
      "properties": {"some_flag": true},
      "object_refs": [],
      "node_tree": {
        "name": "GN_Shell",
        "is_linked": false,
        "library_path": null,
        "inputs": [
          {
            "name": "Bevel",
            "identifier": "Input_2",
            "socket_type": "NodeSocketFloat",
            "default_value": 0.002,
            "min": 0.0,
            "max": 0.1,
            "subtype": "DISTANCE"
          }
        ],
        "outputs": [
          {
            "name": "Geometry",
            "identifier": "Output_1",
            "socket_type": "NodeSocketGeometry"
          }
        ]
      }
    }
  ]
}
```

**Implementation Checklist:**
| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/modeling.py` | `def get_modifier_data(...)` |
| Application | `server/application/tool_handlers/modeling_handler.py` | RPC wrapper + validation |
| Adapter | `server/adapters/mcp/areas/modeling.py` | `@mcp.tool()` exposure |
| Addon | `blender_addon/application/handlers/modeling.py` | Modifier property dump |
| Metadata | `server/router/infrastructure/tools_metadata/modeling/modeling_get_modifier_data.json` | Tool metadata |
| Tests | `tests/unit/tools/modeling/test_get_modifier_data.py` | Modifier props + refs |

---

### TASK-072-2: scene_get_constraints

**Status:** ⏳ TODO

```python
@mcp.tool()
def scene_get_constraints(
    ctx: Context,
    object_name: str,
    include_bones: bool = False
) -> str:
    """
    [OBJECT MODE][READ-ONLY][SAFE] Returns object (and optional bone) constraints.
    """
```

**Return JSON (example):**
```json
{
  "object_name": "Rig",
  "constraints": [
    {"name": "Track", "type": "TRACK_TO", "properties": {"target": "Empty"}}
  ],
  "bone_constraints": []
}
```

**Implementation Checklist:**
| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/scene.py` | `def get_constraints(...)` |
| Application | `server/application/tool_handlers/scene_handler.py` | RPC wrapper + validation |
| Adapter | `server/adapters/mcp/areas/scene.py` | `@mcp.tool()` exposure |
| Addon | `blender_addon/application/handlers/scene.py` | Constraint dump |
| Metadata | `server/router/infrastructure/tools_metadata/scene/scene_get_constraints.json` | Tool metadata |
| Tests | `tests/unit/tools/scene/test_get_constraints.py` | Object + bone constraints |

---

### TASK-072-3: scene_inspect action extensions

**Status:** ⏳ TODO

Add new actions to the existing mega tool (do not remove standalone tools):

- `constraints` → delegates to `scene_get_constraints`
- `modifier_data` → delegates to `modeling_get_modifier_data`

**Notes:**
- Standalone tools remain required for workflow execution and router compatibility.
- Mega tool is a read-only wrapper for context reduction only.

**Files to Update:**
| Layer | File | What to Add |
|-------|------|-------------|
| Adapter | `server/adapters/mcp/areas/scene.py` | Accept new `action` values |
| Metadata | `server/router/infrastructure/tools_metadata/scene/scene_inspect.json` | Update action schema |
| Docs | `_docs/TOOLS/MEGA_TOOLS_ARCHITECTURE.md` | Add new actions |
| Tests | `tests/unit/tools/scene/test_scene_inspect.py` | New action coverage |

---

## ✅ Success Criteria
- Modifier properties can be reconstructed without manual inspection
- Constraints are fully serializable (targets resolved by name)
