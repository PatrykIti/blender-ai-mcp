# TASK-036: Symmetry & Advanced Fill

**Priority:** 🟡 Medium
**Category:** Mesh Tools
**Estimated Effort:** Medium
**Dependencies:** TASK-011 (Edit Mode Foundation)
**Status:** ✅ **Done** (2025-12-05)

---

## Overview

Symmetry and advanced fill tools enable **efficient symmetric modeling and hole filling** - essential for character modeling, architectural elements, and repair workflows.

**Use Cases:**
- Character/creature modeling (left-right symmetry)
- Architectural symmetry
- Filling complex holes with proper topology
- Repair of imported meshes

---

## Sub-Tasks

### TASK-036-1: mesh_symmetrize

**Status:** ✅ Done

Makes mesh symmetric by mirroring one side to the other.

```python
@mcp.tool()
def mesh_symmetrize(
    ctx: Context,
    direction: Literal["NEGATIVE_X", "POSITIVE_X", "NEGATIVE_Y", "POSITIVE_Y", "NEGATIVE_Z", "POSITIVE_Z"] = "NEGATIVE_X",
    threshold: float = 0.0001,
    object_name: str | None = None
) -> str:
    """
    [EDIT MODE][DESTRUCTIVE] Symmetrizes mesh.

    Mirrors geometry from one side to the other, making the mesh perfectly symmetric.
    Useful for:
    - Fixing asymmetric character models
    - Creating symmetric objects from half-models
    - Repair after asymmetric edits

    Direction examples:
    - NEGATIVE_X: Copy from +X to -X (right to left)
    - POSITIVE_X: Copy from -X to +X (left to right)

    Workflow: BEFORE → mesh_select(action="all") to symmetrize entire mesh
    """
```

**Blender API:**
```python
bpy.ops.mesh.symmetrize(direction=direction, threshold=threshold)
```

---

### TASK-036-2: mesh_grid_fill

**Status:** ✅ Done

Fills hole with a grid of quads.

```python
@mcp.tool()
def mesh_grid_fill(
    ctx: Context,
    span: int = 1,
    offset: int = 0,
    use_interp_simple: bool = False,
    object_name: str | None = None
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Fills boundary with grid.

    Unlike mesh_fill_holes (which creates triangles), grid_fill creates
    a proper quad grid - essential for subdivision-ready topology.

    Requirements:
    - Selection must be a closed edge loop (boundary)
    - Works best with even number of edges

    Workflow: BEFORE → mesh_select(action="boundary") to select hole edge
    """
```

**Blender API:**
```python
bpy.ops.mesh.fill_grid(span=span, offset=offset, use_interp_simple=use_interp_simple)
```

---

### TASK-036-3: mesh_poke_faces

**Status:** ✅ Done

Pokes faces (adds vertex at center, creating triangles).

```python
@mcp.tool()
def mesh_poke_faces(
    ctx: Context,
    offset: float = 0.0,
    use_relative_offset: bool = False,
    center_mode: Literal["MEDIAN", "MEDIAN_WEIGHTED", "BOUNDS"] = "MEDIAN_WEIGHTED",
    object_name: str | None = None
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Pokes selected faces.

    Adds a vertex at the center of each selected face and connects to edges,
    creating a fan of triangles. Useful for:
    - Creating spikes/cones
    - Preparing for subdivision patterns
    - Artistic effects

    Workflow: BEFORE → mesh_select faces | Can combine with extrude for spikes
    """
```

**Blender API:**
```python
bpy.ops.mesh.poke(offset=offset, use_relative_offset=use_relative_offset, center_mode=center_mode)
```

---

### TASK-036-4: mesh_beautify_fill

**Status:** ✅ Done

Rearranges triangles to more uniform/aesthetic pattern.

```python
@mcp.tool()
def mesh_beautify_fill(
    ctx: Context,
    angle_limit: float = 180.0,  # degrees
    object_name: str | None = None
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Beautifies face arrangement.

    Rotates triangle edges to create more uniform triangulation.
    Useful after:
    - Boolean operations
    - Triangulation
    - Import cleanup
    """
```

**Blender API:**
```python
bpy.ops.mesh.beautify_fill(angle_limit=math.radians(angle_limit))
```

---

### TASK-036-5: mesh_mirror (Optional)

**Status:** ✅ Done

Mirrors selected geometry within the same object.

```python
@mcp.tool()
def mesh_mirror(
    ctx: Context,
    axis: Literal["X", "Y", "Z"] = "X",
    use_clip: bool = True,
    use_mirror_merge: bool = True,
    merge_threshold: float = 0.001,
    object_name: str | None = None
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Mirrors selected geometry.

    Unlike symmetrize (which replaces one side), mirror creates a copy.
    Useful for:
    - Duplicating symmetric parts
    - Creating mirrored elements

    For non-destructive mirroring, use modeling_add_modifier(type="MIRROR").
    """
```

**Blender API:**
```python
# Set pivot to cursor at origin or object center
bpy.ops.mesh.symmetry_snap()
# Or use transform with negative scale
bpy.ops.transform.mirror(orient_type='GLOBAL', constraint_axis=(axis == 'X', axis == 'Y', axis == 'Z'))
```

---

## Implementation Notes

1. `mesh_symmetrize` works on entire selection - document that selecting all is common
2. `mesh_grid_fill` requires closed boundary loop - validate before operation
3. Consider adding `mesh_select` action for "non_manifold" edges (helps find holes)
4. Return statistics: "Symmetrized X vertices" or "Filled hole with Y quads"

---

## Related Existing Tools

- `mesh_fill_holes` - simple hole filling (triangles)
- `mesh_bridge_edge_loops` - connect two loops
- `modeling_add_modifier(type="MIRROR")` - non-destructive mirror

---

## Testing Requirements

- [x] Unit tests for each tool (39 tests in `tests/unit/tools/mesh/test_mesh_symmetry_fill.py`)
- [x] E2E test: Create asymmetric mesh → symmetrize → verify symmetry
- [x] E2E test: Create hole → grid_fill → verify quad topology
- [x] Test boundary selection requirement for grid_fill
- [x] E2E tests: 28 tests in `tests/e2e/tools/mesh/test_mesh_symmetry_fill.py`

---

## Router Integration

For each tool, create metadata JSON file in `server/router/infrastructure/tools_metadata/mesh/`:

### Example: mesh_symmetrize.json

```json
{
  "tool_name": "mesh_symmetrize",
  "category": "mesh",
  "mode_required": "EDIT",
  "selection_required": false,
  "keywords": ["symmetry", "symmetric", "mirror", "symmetrize", "left right"],
  "sample_prompts": [
    "make the mesh symmetric",
    "mirror the left side to the right",
    "symmetrize the character"
  ],
  "parameters": {
    "direction": {
      "type": "enum",
      "options": ["NEGATIVE_X", "POSITIVE_X", "NEGATIVE_Y", "POSITIVE_Y", "NEGATIVE_Z", "POSITIVE_Z"],
      "default": "NEGATIVE_X"
    },
    "threshold": {"type": "float", "default": 0.0001, "range": [0.0, 0.01]}
  },
  "related_tools": ["mesh_mirror", "modeling_add_modifier"],
  "patterns": [],
  "description": "Makes mesh symmetric by mirroring one side to the other."
}
```

### Example: mesh_grid_fill.json

```json
{
  "tool_name": "mesh_grid_fill",
  "category": "mesh",
  "mode_required": "EDIT",
  "selection_required": true,
  "keywords": ["grid fill", "fill hole", "quad fill", "fill boundary"],
  "sample_prompts": [
    "fill this hole with quads",
    "grid fill the boundary",
    "fill the hole with proper topology"
  ],
  "parameters": {
    "span": {"type": "int", "default": 1, "range": [1, 32]},
    "offset": {"type": "int", "default": 0, "range": [-32, 32]}
  },
  "related_tools": ["mesh_fill_holes", "mesh_bridge_edge_loops", "mesh_select"],
  "patterns": [],
  "description": "Fills boundary with a grid of quads for clean topology."
}
```

---

## Implementation Checklist (per tool)

Each tool requires implementation in **4 layers** + infrastructure:

| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/mesh.py` | `@abstractmethod def tool_name(...)` |
| Application | `server/application/tool_handlers/mesh_handler.py` | `def tool_name(...)` RPC call |
| Adapter | `server/adapters/mcp/areas/mesh.py` | `@mcp.tool() def mesh_tool_name(...)` |
| Addon | `blender_addon/application/handlers/mesh.py` | `def tool_name(...)` with bpy |
| Addon Init | `blender_addon/__init__.py` | Register RPC handler `mesh.tool_name` |
| Dispatcher | `server/adapters/mcp/dispatcher.py` | Add to `_tool_map` (if using router) |
| Router Metadata | `server/router/infrastructure/tools_metadata/mesh/mesh_tool_name.json` | Tool metadata |
| Unit Tests | `tests/unit/tools/mesh/test_tool_name.py` | Handler tests |
| E2E Tests | `tests/e2e/tools/mesh/test_tool_name.py` | Full integration tests |

---

## Documentation Updates Required

After implementing these tools, update:

| File | What to Update |
|------|----------------|
| `_docs/_TASKS/TASK-036_Symmetry_Advanced_Fill.md` | Mark sub-tasks as ✅ Done |
| `_docs/_TASKS/README.md` | Move task to Done section |
| `_docs/_CHANGELOG/{NN}-{date}-symmetry-fill-tools.md` | Create changelog entry |
| `_docs/_MCP_SERVER/README.md` | Add tools to MCP tools table |
| `_docs/_ADDON/README.md` | Add RPC commands to handler table |
| `_docs/AVAILABLE_TOOLS_SUMMARY.md` | Add tools with arguments |
| `_docs/MESH_TOOLS_ARCHITECTURE.md` | Add Symmetry & Fill section |
| `README.md` | Update roadmap checkboxes, add to autoApprove lists |
