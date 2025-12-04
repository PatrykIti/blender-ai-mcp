# TASK-044: Extraction Analysis Tools

**Priority:** 🔴 High
**Category:** Extraction Tools (New Area)
**Estimated Effort:** Large
**Dependencies:** TASK-042 (Automatic Workflow Extraction System), TASK-043 (Scene Utility Tools)
**Status:** ✅ **COMPLETED** (2025-12-04)

---

## Overview

Specialized analysis tools for the Automatic Workflow Extraction System. These tools enable deep topology analysis, component detection, symmetry detection, and multi-angle rendering for LLM Vision integration.

**Use Cases:**
- Analyzing imported 3D models for workflow extraction
- Detecting mesh features (bevels, insets, extrusions)
- Component separation and symmetry detection
- Multi-angle rendering for LLM-based semantic analysis

**New MCP Area:** `extraction` - dedicated area for workflow extraction tools

---

## Architecture

```
server/adapters/mcp/areas/
├── extraction.py              # NEW: MCP tool definitions

server/domain/tools/
├── extraction.py              # NEW: IExtractionTool interface

server/application/tool_handlers/
├── extraction_handler.py      # NEW: RPC bridge

blender_addon/application/handlers/
├── extraction.py              # NEW: Blender-side analysis (bpy calls)
```

---

## Sub-Tasks

### TASK-044-1: extraction_deep_topology

**Status:** ✅ Done

Extended topology analysis beyond `scene_inspect(action="topology")`.

```python
@mcp.tool()
def extraction_deep_topology(
    ctx: Context,
    object_name: str
) -> str:
    """
    [OBJECT MODE][READ-ONLY][SAFE] Deep topology analysis for workflow extraction.

    Workflow: START → extraction pipeline | USE FOR → detecting mesh features

    Returns detailed analysis including:
    - Vertex/edge/face counts and types (tris/quads/ngons)
    - Edge loop detection and count
    - Face coplanarity groups
    - Vertex distribution (clustering)
    - Estimated base primitive
    - Feature indicators (beveled edges, inset faces, etc.)

    Args:
        object_name: Name of the mesh object to analyze

    Returns:
        JSON with extended topology data
    """
```

**Blender API:**
```python
import bmesh

obj = bpy.data.objects.get(object_name)
bm = bmesh.new()
bm.from_mesh(obj.data)

# Edge loop detection
edge_loops = []
for edge in bm.edges:
    if edge.is_boundary:
        # boundary edge detection
        pass
    # Check for continuous edge loops

# Face coplanarity analysis
face_groups = []
for face in bm.faces:
    normal = face.normal
    # Group faces by similar normals

# Vertex clustering
from mathutils import kdtree
kd = kdtree.KDTree(len(bm.verts))
# Build spatial index for clustering

bm.free()
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/extraction.py` | `class IExtractionTool(ABC)` + `@abstractmethod def deep_topology(...)` |
| Application | `server/application/tool_handlers/extraction_handler.py` | `class ExtractionToolHandler` + `def deep_topology(...)` RPC call |
| Adapter | `server/adapters/mcp/areas/extraction.py` | `@mcp.tool() def extraction_deep_topology(...)` |
| Addon | `blender_addon/application/handlers/extraction.py` | `class ExtractionHandler` + `def deep_topology(...)` with bmesh analysis |
| Addon Init | `blender_addon/__init__.py` | Import ExtractionHandler, register RPC handlers |
| Router Metadata | `server/router/infrastructure/tools_metadata/extraction/extraction_deep_topology.json` | Tool metadata |
| Unit Tests | `tests/unit/tools/extraction/test_deep_topology.py` | Handler tests |
| E2E Tests | `tests/e2e/tools/extraction/test_deep_topology.py` | Full integration tests |

---

### TASK-044-2: extraction_component_separate

**Status:** ✅ Done

Separates mesh into loose parts (components) for individual analysis.

```python
@mcp.tool()
def extraction_component_separate(
    ctx: Context,
    object_name: str,
    min_vertex_count: int = 4
) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Separates mesh into loose parts.

    Workflow: AFTER → import model | BEFORE → per-component analysis

    Creates separate objects for each disconnected mesh island.
    Filters out tiny components (less than min_vertex_count vertices).

    Args:
        object_name: Name of the mesh object to separate
        min_vertex_count: Minimum vertices to keep component (default 4)

    Returns:
        JSON with list of created component names and their stats
    """
```

**Blender API:**
```python
# Select object
obj = bpy.data.objects.get(object_name)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)

# Enter edit mode and select all
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')

# Separate by loose parts
bpy.ops.mesh.separate(type='LOOSE')

bpy.ops.object.mode_set(mode='OBJECT')

# Get all new objects (they share the base name)
components = [o for o in bpy.data.objects if o.name.startswith(object_name)]
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/extraction.py` | `@abstractmethod def component_separate(...)` |
| Application | `server/application/tool_handlers/extraction_handler.py` | `def component_separate(...)` RPC call |
| Adapter | `server/adapters/mcp/areas/extraction.py` | `@mcp.tool() def extraction_component_separate(...)` |
| Addon | `blender_addon/application/handlers/extraction.py` | `def component_separate(...)` with bpy.ops |
| Addon Init | `blender_addon/__init__.py` | Register RPC handler `extraction.component_separate` |
| Router Metadata | `server/router/infrastructure/tools_metadata/extraction/extraction_component_separate.json` | Tool metadata |
| Unit Tests | `tests/unit/tools/extraction/test_component_separate.py` | Handler tests |
| E2E Tests | `tests/e2e/tools/extraction/test_component_separate.py` | Full integration tests |

---

### TASK-044-3: extraction_detect_symmetry

**Status:** ✅ Done

Detects symmetry planes in a mesh object.

```python
@mcp.tool()
def extraction_detect_symmetry(
    ctx: Context,
    object_name: str,
    tolerance: float = 0.001
) -> str:
    """
    [OBJECT MODE][READ-ONLY][SAFE] Detects symmetry in mesh geometry.

    Workflow: AFTER → component_separate | USE FOR → mirror modifier detection

    Checks for symmetry along X, Y, Z axes by comparing vertex positions.
    Reports symmetry confidence for each axis.

    Args:
        object_name: Name of the mesh object to analyze
        tolerance: Distance tolerance for symmetry matching (default 0.001)

    Returns:
        JSON with symmetry info:
        {
            "x_symmetric": true,
            "x_confidence": 0.98,
            "y_symmetric": false,
            "y_confidence": 0.12,
            "z_symmetric": false,
            "z_confidence": 0.05,
            "symmetric_pairs": 124,
            "total_vertices": 256
        }
    """
```

**Blender API:**
```python
import bmesh
from mathutils import kdtree

obj = bpy.data.objects.get(object_name)
bm = bmesh.new()
bm.from_mesh(obj.data)

# Build KD tree for efficient lookup
kd = kdtree.KDTree(len(bm.verts))
for i, v in enumerate(bm.verts):
    kd.insert(v.co, i)
kd.balance()

# Check X symmetry
x_matches = 0
for v in bm.verts:
    mirror_co = (-v.co.x, v.co.y, v.co.z)
    co, idx, dist = kd.find(mirror_co)
    if dist < tolerance:
        x_matches += 1

x_confidence = x_matches / len(bm.verts)
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/extraction.py` | `@abstractmethod def detect_symmetry(...)` |
| Application | `server/application/tool_handlers/extraction_handler.py` | `def detect_symmetry(...)` RPC call |
| Adapter | `server/adapters/mcp/areas/extraction.py` | `@mcp.tool() def extraction_detect_symmetry(...)` |
| Addon | `blender_addon/application/handlers/extraction.py` | `def detect_symmetry(...)` with bmesh + kdtree |
| Addon Init | `blender_addon/__init__.py` | Register RPC handler `extraction.detect_symmetry` |
| Router Metadata | `server/router/infrastructure/tools_metadata/extraction/extraction_detect_symmetry.json` | Tool metadata |
| Unit Tests | `tests/unit/tools/extraction/test_detect_symmetry.py` | Handler tests |
| E2E Tests | `tests/e2e/tools/extraction/test_detect_symmetry.py` | Full integration tests |

---

### TASK-044-4: extraction_edge_loop_analysis

**Status:** ✅ Done

Analyzes edge loops to detect bevels, subdivisions, and support loops.

```python
@mcp.tool()
def extraction_edge_loop_analysis(
    ctx: Context,
    object_name: str
) -> str:
    """
    [OBJECT MODE][READ-ONLY][SAFE] Analyzes edge loops for feature detection.

    Workflow: AFTER → deep_topology | USE FOR → bevel/subdivision detection

    Detects:
    - Parallel edge loops (indicator of bevel or subdivision)
    - Edge loop spacing patterns
    - Support loops near corners
    - Chamfered edges

    Args:
        object_name: Name of the mesh object to analyze

    Returns:
        JSON with edge loop analysis:
        {
            "total_edge_loops": 12,
            "parallel_loop_groups": [
                {"count": 3, "spacing": 0.05, "likely_feature": "bevel"},
                {"count": 2, "spacing": 0.1, "likely_feature": "subdivision"}
            ],
            "corner_support_loops": 4,
            "estimated_bevel_segments": 2,
            "has_chamfer": true
        }
    """
```

**Blender API:**
```python
import bmesh

bm = bmesh.new()
bm.from_mesh(obj.data)

# Find edge loops using edge walking
def find_edge_loop(start_edge):
    loop = [start_edge]
    # Walk edges that share exactly 2 faces with similar normals
    # Continue until loop closes or ends
    return loop

# Analyze spacing between parallel loops
def analyze_loop_spacing(loops):
    # Calculate distance between parallel edge loops
    # Detect regular patterns (bevel segments, subdivisions)
    pass
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/extraction.py` | `@abstractmethod def edge_loop_analysis(...)` |
| Application | `server/application/tool_handlers/extraction_handler.py` | `def edge_loop_analysis(...)` RPC call |
| Adapter | `server/adapters/mcp/areas/extraction.py` | `@mcp.tool() def extraction_edge_loop_analysis(...)` |
| Addon | `blender_addon/application/handlers/extraction.py` | `def edge_loop_analysis(...)` with bmesh analysis |
| Addon Init | `blender_addon/__init__.py` | Register RPC handler `extraction.edge_loop_analysis` |
| Router Metadata | `server/router/infrastructure/tools_metadata/extraction/extraction_edge_loop_analysis.json` | Tool metadata |
| Unit Tests | `tests/unit/tools/extraction/test_edge_loop_analysis.py` | Handler tests |
| E2E Tests | `tests/e2e/tools/extraction/test_edge_loop_analysis.py` | Full integration tests |

---

### TASK-044-5: extraction_face_group_analysis

**Status:** ✅ Done

Analyzes face groups to detect insets, extrusions, and planar regions.

```python
@mcp.tool()
def extraction_face_group_analysis(
    ctx: Context,
    object_name: str,
    angle_threshold: float = 5.0
) -> str:
    """
    [OBJECT MODE][READ-ONLY][SAFE] Analyzes face groups for feature detection.

    Workflow: AFTER → deep_topology | USE FOR → inset/extrude detection

    Groups faces by:
    - Normal direction (coplanar faces)
    - Height/position (Z-level groups)
    - Connectivity (adjacent face regions)

    Detects:
    - Inset faces (face surrounded by thin quad border)
    - Extruded regions (face groups at different heights)
    - Planar regions (large coplanar face groups)

    Args:
        object_name: Name of the mesh object to analyze
        angle_threshold: Max angle difference for coplanar grouping (degrees)

    Returns:
        JSON with face group analysis:
        {
            "face_groups": [
                {"id": 0, "face_count": 24, "normal": [0,0,1], "avg_height": 1.0},
                {"id": 1, "face_count": 4, "normal": [0,0,1], "avg_height": 0.9, "likely_inset": true}
            ],
            "detected_insets": 2,
            "detected_extrusions": 3,
            "height_levels": [0.0, 0.5, 1.0]
        }
    """
```

**Blender API:**
```python
import bmesh
from collections import defaultdict

bm = bmesh.new()
bm.from_mesh(obj.data)

# Group faces by normal
normal_groups = defaultdict(list)
for face in bm.faces:
    # Round normal to detect coplanar faces
    key = tuple(round(n, 2) for n in face.normal)
    normal_groups[key].append(face)

# Detect inset patterns
def detect_inset(face_group):
    # Check if face is surrounded by thin quad border
    # Thin = face area is small relative to perimeter
    pass

# Detect extrusion patterns
def detect_extrusion(face_groups):
    # Check for face groups at different Z levels with same normal
    pass
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/extraction.py` | `@abstractmethod def face_group_analysis(...)` |
| Application | `server/application/tool_handlers/extraction_handler.py` | `def face_group_analysis(...)` RPC call |
| Adapter | `server/adapters/mcp/areas/extraction.py` | `@mcp.tool() def extraction_face_group_analysis(...)` |
| Addon | `blender_addon/application/handlers/extraction.py` | `def face_group_analysis(...)` with bmesh analysis |
| Addon Init | `blender_addon/__init__.py` | Register RPC handler `extraction.face_group_analysis` |
| Router Metadata | `server/router/infrastructure/tools_metadata/extraction/extraction_face_group_analysis.json` | Tool metadata |
| Unit Tests | `tests/unit/tools/extraction/test_face_group_analysis.py` | Handler tests |
| E2E Tests | `tests/e2e/tools/extraction/test_face_group_analysis.py` | Full integration tests |

---

### TASK-044-6: extraction_render_angles

**Status:** ✅ Done

Renders object from multiple angles for LLM Vision analysis.

```python
@mcp.tool()
def extraction_render_angles(
    ctx: Context,
    object_name: str,
    angles: list[str] = ["front", "back", "left", "right", "top", "iso"],
    resolution: int = 512,
    output_dir: str = "/tmp/extraction_renders"
) -> str:
    """
    [OBJECT MODE][SAFE] Renders object from multiple angles for LLM analysis.

    Workflow: AFTER → component analysis | USE FOR → LLM Vision semantic extraction

    Renders the object from predefined angles:
    - front: Y- direction
    - back: Y+ direction
    - left: X- direction
    - right: X+ direction
    - top: Z+ direction (looking down)
    - iso: Isometric view (45° from front-right-top)

    Args:
        object_name: Object to render (others will be hidden)
        angles: List of angles to render (default: all 6)
        resolution: Image resolution in pixels (default 512)
        output_dir: Directory to save renders

    Returns:
        JSON with render paths:
        {
            "renders": [
                {"angle": "front", "path": "/tmp/extraction_renders/Phone_front.png"},
                {"angle": "iso", "path": "/tmp/extraction_renders/Phone_iso.png"}
            ],
            "object_name": "Phone",
            "resolution": 512
        }
    """
```

**Blender API:**
```python
import os
from mathutils import Vector, Euler
import math

# Angle presets (camera location relative to object)
ANGLE_PRESETS = {
    "front": {"location": (0, -5, 0), "rotation": (math.pi/2, 0, 0)},
    "back": {"location": (0, 5, 0), "rotation": (math.pi/2, 0, math.pi)},
    "left": {"location": (-5, 0, 0), "rotation": (math.pi/2, 0, -math.pi/2)},
    "right": {"location": (5, 0, 0), "rotation": (math.pi/2, 0, math.pi/2)},
    "top": {"location": (0, 0, 5), "rotation": (0, 0, 0)},
    "iso": {"location": (3.5, -3.5, 3.5), "rotation": (math.pi/4, 0, math.pi/4)},
}

# Create/get camera
cam = bpy.data.cameras.new("ExtractCam")
cam_obj = bpy.data.objects.new("ExtractCam", cam)
bpy.context.scene.collection.objects.link(cam_obj)

# Hide all except target
for obj in bpy.data.objects:
    obj.hide_render = (obj.name != object_name and obj.type == 'MESH')

# Render each angle
for angle_name in angles:
    preset = ANGLE_PRESETS[angle_name]
    cam_obj.location = preset["location"]
    cam_obj.rotation_euler = preset["rotation"]

    bpy.context.scene.camera = cam_obj
    bpy.context.scene.render.resolution_x = resolution
    bpy.context.scene.render.resolution_y = resolution
    bpy.context.scene.render.filepath = f"{output_dir}/{object_name}_{angle_name}.png"
    bpy.ops.render.render(write_still=True)
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/domain/tools/extraction.py` | `@abstractmethod def render_angles(...)` |
| Application | `server/application/tool_handlers/extraction_handler.py` | `def render_angles(...)` RPC call |
| Adapter | `server/adapters/mcp/areas/extraction.py` | `@mcp.tool() def extraction_render_angles(...)` |
| Addon | `blender_addon/application/handlers/extraction.py` | `def render_angles(...)` with bpy.ops.render |
| Addon Init | `blender_addon/__init__.py` | Register RPC handler `extraction.render_angles` |
| Router Metadata | `server/router/infrastructure/tools_metadata/extraction/extraction_render_angles.json` | Tool metadata |
| Unit Tests | `tests/unit/tools/extraction/test_render_angles.py` | Handler tests |
| E2E Tests | `tests/e2e/tools/extraction/test_render_angles.py` | Full integration tests |

---

## Testing Requirements

- [x] Unit tests for each tool handler (27 tests total)
- [x] E2E tests for each tool with Blender integration (7 test files)
- [x] E2E test: Full extraction pipeline (import → analyze → separate → detect features)
- [ ] Test with POC models: simple cube, phone, tower, etc.

---

## Implementation Order

Recommended implementation order based on dependencies:

1. **extraction_deep_topology** (foundation - basic analysis)
2. **extraction_component_separate** (needed for multi-part models)
3. **extraction_detect_symmetry** (independent, useful for mirror detection)
4. **extraction_edge_loop_analysis** (depends on topology understanding)
5. **extraction_face_group_analysis** (depends on topology understanding)
6. **extraction_render_angles** (independent, for LLM Vision phase)

---

## New Files to Create

### Server Side
```
server/domain/tools/extraction.py                              # Interface
server/application/tool_handlers/extraction_handler.py         # RPC bridge
server/adapters/mcp/areas/extraction.py                        # MCP tools
server/router/infrastructure/tools_metadata/extraction/        # Metadata dir
  ├── extraction_deep_topology.json
  ├── extraction_component_separate.json
  ├── extraction_detect_symmetry.json
  ├── extraction_edge_loop_analysis.json
  ├── extraction_face_group_analysis.json
  └── extraction_render_angles.json
```

### Blender Addon
```
blender_addon/application/handlers/extraction.py               # Blender analysis
```

### Tests
```
tests/unit/tools/extraction/
  ├── __init__.py
  ├── test_deep_topology.py
  ├── test_component_separate.py
  ├── test_detect_symmetry.py
  ├── test_edge_loop_analysis.py
  ├── test_face_group_analysis.py
  └── test_render_angles.py

tests/e2e/tools/extraction/
  ├── __init__.py
  ├── test_deep_topology.py
  ├── test_component_separate.py
  ├── test_detect_symmetry.py
  ├── test_edge_loop_analysis.py
  ├── test_face_group_analysis.py
  ├── test_render_angles.py
  └── test_extraction_pipeline.py
```

---

## Documentation Updates Required

After implementing these tools, update:

| File | What to Update |
|------|----------------|
| `_docs/_TASKS/TASK-044_Extraction_Analysis_Tools.md` | Mark sub-tasks as ✅ Done |
| `_docs/_TASKS/README.md` | Add TASK-044 to task list, update statistics |
| `_docs/_CHANGELOG/{NN}-{date}-extraction-tools.md` | Create changelog entry |
| `_docs/_MCP_SERVER/README.md` | Add new `extraction` area and tools to MCP tools table |
| `_docs/_ADDON/README.md` | Add `extraction` RPC commands to handler table |
| `_docs/AVAILABLE_TOOLS_SUMMARY.md` | Add extraction tools with arguments |
| `_docs/EXTRACTION_TOOLS_ARCHITECTURE.md` | **CREATE**: New architecture doc for extraction area |
| `README.md` | Add extraction tools to roadmap, add to autoApprove lists |
| `_docs/_TASKS/TASK-042_Automatic_Workflow_Extraction_System.md` | Update Phase 1 status when tools ready |

---

## Router Integration

Create metadata directory and files:

```bash
mkdir -p server/router/infrastructure/tools_metadata/extraction/
```

### Example: extraction_deep_topology.json

```json
{
  "tool_name": "extraction_deep_topology",
  "category": "extraction",
  "mode_required": "OBJECT",
  "selection_required": false,
  "keywords": ["topology", "analyze", "mesh analysis", "vertex count", "edge loops", "features"],
  "sample_prompts": [
    "analyze the mesh topology",
    "get detailed mesh information",
    "what features does this mesh have"
  ],
  "parameters": {
    "object_name": {"type": "string", "required": true, "description": "Object to analyze"}
  },
  "related_tools": ["scene_inspect", "extraction_edge_loop_analysis", "extraction_face_group_analysis"],
  "patterns": [],
  "description": "Deep topology analysis for workflow extraction."
}
```

---

## MCP Server Registration

Add to `server/adapters/mcp/server.py`:

```python
from server.adapters.mcp.areas import extraction

# In register_tools():
extraction.register_extraction_tools(mcp)
```

---

## Relation to TASK-042

TASK-044 implements the **Phase 1** tools defined in TASK-042:
- These tools provide the foundation for the Automatic Workflow Extraction System
- After TASK-044, Phase 2-6 of TASK-042 can proceed with workflow generation logic

```
TASK-044 (Tools) → TASK-042 Phase 2-6 (Workflow Generation Logic)
```
