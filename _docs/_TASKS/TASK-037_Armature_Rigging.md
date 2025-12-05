# TASK-037: Armature & Rigging ✅

**Priority:** 🟢 Low (Future)
**Category:** Animation / Rigging
**Estimated Effort:** High
**Dependencies:** TASK-017 (Vertex Groups)
**Status:** ✅ Done

---

## Overview

Armature and rigging tools enable **skeletal animation** - essential for character animation, mechanical rigs, and procedural motion.

**Use Cases:**
- Character rigging for games/film
- Mechanical rig (robot arms, machines)
- Procedural animation setups
- Auto-rigging workflows

**Note:** This is a complex domain. Start with basic tools, expand based on demand.

---

## Sub-Tasks

### TASK-037-1: armature_create

**Status:** ✅ Done

Creates an armature object with initial bone.

```python
@mcp.tool()
def armature_create(
    ctx: Context,
    name: str = "Armature",
    location: list[float] | None = None,
    bone_name: str = "Bone",
    bone_length: float = 1.0
) -> str:
    """
    [OBJECT MODE][SCENE] Creates armature with initial bone.

    Armature is a skeleton structure for deforming meshes.
    After creation, add more bones with armature_add_bone.

    Workflow: AFTER → armature_add_bone | armature_bind
    """
```

**Blender API:**
```python
bpy.ops.object.armature_add(location=location or (0, 0, 0))
armature = bpy.context.active_object
armature.name = name
armature.data.bones[0].name = bone_name
```

---

### TASK-037-2: armature_add_bone

**Status:** ✅ Done

Adds a new bone to existing armature.

```python
@mcp.tool()
def armature_add_bone(
    ctx: Context,
    armature_name: str,
    bone_name: str,
    head: list[float],  # [x, y, z] start position
    tail: list[float],  # [x, y, z] end position
    parent_bone: str | None = None,
    use_connect: bool = False  # Connect to parent (no gap)
) -> str:
    """
    [EDIT MODE on armature] Adds bone to armature.

    Bones can be parented to create hierarchy:
    - Spine → Chest → Neck → Head
    - Shoulder → Upper Arm → Forearm → Hand → Fingers

    Workflow: BEFORE → armature_create or existing armature
    """
```

**Blender API:**
```python
armature = bpy.data.objects[armature_name]
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='EDIT')

bone = armature.data.edit_bones.new(bone_name)
bone.head = head
bone.tail = tail

if parent_bone:
    bone.parent = armature.data.edit_bones[parent_bone]
    bone.use_connect = use_connect

bpy.ops.object.mode_set(mode='OBJECT')
```

---

### TASK-037-3: armature_bind

**Status:** ✅ Done

Binds mesh to armature (automatic weights).

```python
@mcp.tool()
def armature_bind(
    ctx: Context,
    mesh_name: str,
    armature_name: str,
    bind_type: Literal["AUTO", "ENVELOPE", "EMPTY"] = "AUTO"
) -> str:
    """
    [OBJECT MODE] Binds mesh to armature with automatic weights.

    Bind types:
    - AUTO: Automatic weight calculation (best for organic)
    - ENVELOPE: Use bone envelopes for weights
    - EMPTY: Create modifier without weights (manual painting)

    Creates Armature modifier and vertex groups for each bone.

    Workflow: BEFORE → Mesh and armature positioned correctly
    """
```

**Blender API:**
```python
mesh = bpy.data.objects[mesh_name]
armature = bpy.data.objects[armature_name]

# Select mesh, then armature (armature must be active)
bpy.ops.object.select_all(action='DESELECT')
mesh.select_set(True)
armature.select_set(True)
bpy.context.view_layer.objects.active = armature

if bind_type == "AUTO":
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
elif bind_type == "ENVELOPE":
    bpy.ops.object.parent_set(type='ARMATURE_ENVELOPE')
else:
    bpy.ops.object.parent_set(type='ARMATURE')
```

---

### TASK-037-4: armature_pose_bone

**Status:** ✅ Done

Poses a bone (rotation/location).

```python
@mcp.tool()
def armature_pose_bone(
    ctx: Context,
    armature_name: str,
    bone_name: str,
    rotation: list[float] | None = None,  # Euler XYZ in degrees
    location: list[float] | None = None,
    scale: list[float] | None = None
) -> str:
    """
    [POSE MODE] Poses armature bone.

    For animation, use keyframe tools (future).
    This tool sets the current pose without keyframing.
    """
```

**Blender API:**
```python
armature = bpy.data.objects[armature_name]
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='POSE')

bone = armature.pose.bones[bone_name]
if rotation:
    bone.rotation_euler = [math.radians(r) for r in rotation]
if location:
    bone.location = location
if scale:
    bone.scale = scale
```

---

### TASK-037-5: armature_weight_paint_assign

**Status:** ✅ Done

Assigns weights to vertex group (for manual rigging).

```python
@mcp.tool()
def weight_paint_assign(
    ctx: Context,
    object_name: str,
    vertex_group: str,
    weight: float = 1.0,
    mode: Literal["REPLACE", "ADD", "SUBTRACT"] = "REPLACE"
) -> str:
    """
    [WEIGHT PAINT MODE / EDIT MODE][SELECTION-BASED] Assigns weights to selection.

    For precise control over bone deformation influence.
    Use after armature_bind with EMPTY weights.
    """
```

---

## Implementation Notes

1. **Mode handling**: Armature editing requires EDIT mode on armature, posing requires POSE mode
2. **Automatic weights**: Can fail on complex meshes - return warning
3. **Vertex groups**: armature_bind creates groups matching bone names
4. Consider integration with existing `mesh_create_vertex_group` and `mesh_assign_to_group`

---

## Complexity Warning

Rigging is one of the most complex areas in 3D:
- Bone chains and IK (Inverse Kinematics)
- Constraints (Copy Rotation, Limit, etc.)
- Shape keys for facial animation
- Drivers for procedural motion

Start simple, expand based on user demand.

---

## Testing Requirements

- [x] Unit tests with mocked armature operations
- [x] E2E test: Create armature → add bones → bind mesh → pose → verify deformation
- [x] Test automatic weights on simple mesh (cube)
- [x] Test manual weight assignment workflow

---

## Router Integration

For each tool, create metadata JSON file in `server/router/infrastructure/tools_metadata/armature/`:

### Example: armature_create.json

```json
{
  "tool_name": "armature_create",
  "category": "armature",
  "mode_required": "OBJECT",
  "selection_required": false,
  "keywords": ["armature", "skeleton", "bone", "rig", "rigging"],
  "sample_prompts": [
    "create an armature",
    "add skeleton for rigging",
    "create bones for the character"
  ],
  "parameters": {
    "name": {"type": "string", "default": "Armature"},
    "bone_name": {"type": "string", "default": "Bone"},
    "bone_length": {"type": "float", "default": 1.0, "range": [0.01, 100.0]}
  },
  "related_tools": ["armature_add_bone", "armature_bind"],
  "patterns": [],
  "description": "Creates an armature object with initial bone for rigging."
}
```

### Example: armature_bind.json

```json
{
  "tool_name": "armature_bind",
  "category": "armature",
  "mode_required": "OBJECT",
  "selection_required": false,
  "keywords": ["bind", "parent", "skin", "weight", "deform", "rig"],
  "sample_prompts": [
    "bind the mesh to the armature",
    "attach skeleton to character",
    "apply automatic weights"
  ],
  "parameters": {
    "mesh_name": {"type": "string", "description": "Mesh to bind"},
    "armature_name": {"type": "string", "description": "Armature to bind to"},
    "bind_type": {
      "type": "enum",
      "options": ["AUTO", "ENVELOPE", "EMPTY"],
      "default": "AUTO"
    }
  },
  "related_tools": ["armature_create", "armature_pose_bone", "mesh_create_vertex_group"],
  "patterns": [],
  "description": "Binds mesh to armature with automatic weight calculation."
}
```

---

## Implementation Checklist (per tool)

Each tool requires implementation in **4 layers** + infrastructure:

| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/armature.py` | `@abstractmethod def tool_name(...)` (NEW FILE) |
| Application | `server/application/tool_handlers/armature_handler.py` | `def tool_name(...)` RPC call (NEW FILE) |
| Adapter | `server/adapters/mcp/areas/armature.py` | `@mcp.tool() def armature_tool_name(...)` (NEW FILE) |
| Addon | `blender_addon/application/handlers/armature.py` | `def tool_name(...)` with bpy (NEW FILE) |
| Addon Init | `blender_addon/__init__.py` | Register RPC handler `armature.tool_name` |
| Dispatcher | `server/adapters/mcp/dispatcher.py` | Add `get_armature_handler()` + tool mappings |
| DI Provider | `server/infrastructure/di.py` | Add `get_armature_handler()` (NEW) |
| Router Metadata | `server/router/infrastructure/tools_metadata/armature/armature_tool_name.json` | Tool metadata (NEW DIR) |
| Unit Tests | `tests/unit/tools/armature/test_tool_name.py` | Handler tests (NEW DIR) |
| E2E Tests | `tests/e2e/tools/armature/test_tool_name.py` | Full integration tests (NEW DIR) |

---

## Documentation Updates Required

After implementing these tools, update:

| File | What to Update |
|------|----------------|
| `_docs/_TASKS/TASK-037_Armature_Rigging.md` | Mark sub-tasks as ✅ Done |
| `_docs/_TASKS/README.md` | Move task to Done section |
| `_docs/_CHANGELOG/{NN}-{date}-armature-tools.md` | Create changelog entry |
| `_docs/_MCP_SERVER/README.md` | Add tools to MCP tools table |
| `_docs/_ADDON/README.md` | Add RPC commands to handler table |
| `_docs/AVAILABLE_TOOLS_SUMMARY.md` | Add tools with arguments |
| `README.md` | Update roadmap checkboxes, add to autoApprove lists |
