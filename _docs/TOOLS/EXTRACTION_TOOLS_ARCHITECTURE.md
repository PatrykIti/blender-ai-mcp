# Extraction Tools Architecture

Analysis tools for the **Automatic Workflow Extraction System** (TASK-042). These tools enable deep topology analysis, component detection, symmetry detection, and multi-angle rendering for LLM Vision integration.

## Purpose

The extraction tools are designed to analyze existing 3D models and reverse-engineer the modeling steps that were likely used to create them. This enables:

1. **Workflow Learning**: Understand how models were constructed
2. **Automatic Workflow Generation**: Create reproducible modeling workflows from reference models
3. **LLM Vision Integration**: Provide multi-angle renders for semantic analysis

## Tool Overview

| Tool | Mode | Type | Description |
|------|------|------|-------------|
| `extraction_deep_topology` | Object | READ-ONLY | Deep topology analysis with feature detection |
| `extraction_component_separate` | Object | DESTRUCTIVE | Separates mesh into loose parts |
| `extraction_detect_symmetry` | Object | READ-ONLY | Detects symmetry planes using KDTree |
| `extraction_edge_loop_analysis` | Object | READ-ONLY | Analyzes edge loops and patterns |
| `extraction_face_group_analysis` | Object | READ-ONLY | Analyzes face groups by normal/height |
| `extraction_render_angles` | Object | SAFE | Multi-angle renders for LLM Vision |

---

## Tool Details

### `extraction_deep_topology`

**Tags:** `[OBJECT MODE][READ-ONLY][SAFE]`

Deep topology analysis that provides:
- Vertex/edge/face counts and types (tris/quads/ngons)
- Edge loop detection and count
- Face coplanarity groups
- **Base primitive detection** (CUBE, PLANE, CYLINDER, SPHERE, CUSTOM) with confidence scores
- **Feature indicators** (beveled edges, inset faces, extrusions)

**Arguments:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `object_name` | str | required | Name of the mesh object to analyze |

**Returns:** JSON with topology data including:
```json
{
  "object_name": "Cube",
  "vertex_count": 8,
  "edge_count": 12,
  "face_count": 6,
  "tri_count": 0,
  "quad_count": 6,
  "ngon_count": 0,
  "detected_primitive": "CUBE",
  "primitive_confidence": 0.95,
  "features": {
    "has_beveled_edges": false,
    "has_inset_faces": false,
    "has_extrusions": false,
    "bevel_edge_count": 0,
    "inset_face_count": 0
  }
}
```

**Workflow:** `START → extraction pipeline`

---

### `extraction_component_separate`

**Tags:** `[OBJECT MODE][DESTRUCTIVE]`

Separates a mesh into its loose parts (disconnected mesh islands). Useful for analyzing complex models with multiple components.

**Arguments:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `object_name` | str | required | Name of the mesh object to separate |
| `min_vertex_count` | int | 4 | Minimum vertices to keep component |

**Returns:** JSON with component list:
```json
{
  "original_object": "ComplexModel",
  "component_count": 3,
  "components": [
    {
      "name": "ComplexModel_component_0",
      "vertex_count": 156,
      "bounding_box": {"min": [-1, -1, 0], "max": [1, 1, 2]},
      "centroid": [0, 0, 1]
    }
  ]
}
```

**Workflow:** `AFTER → import model | BEFORE → per-component analysis`

---

### `extraction_detect_symmetry`

**Tags:** `[OBJECT MODE][READ-ONLY][SAFE]`

Detects mesh symmetry along X, Y, Z axes using KDTree for efficient vertex matching. Reports confidence scores per axis.

**Arguments:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `object_name` | str | required | Name of the mesh object to analyze |
| `tolerance` | float | 0.001 | Distance tolerance for symmetry matching |

**Returns:** JSON with symmetry info:
```json
{
  "object_name": "Phone",
  "vertex_count": 248,
  "x_symmetric": true,
  "x_confidence": 0.98,
  "x_matched_pairs": 120,
  "y_symmetric": false,
  "y_confidence": 0.45,
  "y_matched_pairs": 56,
  "z_symmetric": false,
  "z_confidence": 0.12,
  "z_matched_pairs": 15
}
```

**Workflow:** `AFTER → component_separate | USE FOR → mirror modifier detection`

---

### `extraction_edge_loop_analysis`

**Tags:** `[OBJECT MODE][READ-ONLY][SAFE]`

Analyzes edge loops for feature detection including:
- Parallel edge loops (indicator of bevel or subdivision)
- Edge loop spacing patterns
- Support loops near corners
- Chamfered edges
- Boundary/manifold/non-manifold edge classification

**Arguments:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `object_name` | str | required | Name of the mesh object to analyze |

**Returns:** JSON with edge loop analysis:
```json
{
  "object_name": "BeveledCube",
  "total_edges": 48,
  "boundary_edges": 0,
  "manifold_edges": 48,
  "non_manifold_edges": 0,
  "total_edge_loops": 12,
  "parallel_loop_groups": [
    {"axis": "X", "loop_count": 4, "spacing": 0.25},
    {"axis": "Z", "loop_count": 4, "spacing": 0.25}
  ],
  "chamfer_edges_detected": true,
  "chamfer_edge_count": 24
}
```

**Workflow:** `AFTER → deep_topology | USE FOR → bevel/subdivision detection`

---

### `extraction_face_group_analysis`

**Tags:** `[OBJECT MODE][READ-ONLY][SAFE]`

Groups faces by normal direction and height, detecting:
- Coplanar face groups
- Height-level groups (Z-level)
- Inset faces (face surrounded by thin quad border)
- Extruded regions (face groups at different heights)

**Arguments:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `object_name` | str | required | Name of the mesh object to analyze |
| `angle_threshold` | float | 5.0 | Max angle difference for coplanar grouping (degrees) |

**Returns:** JSON with face group analysis:
```json
{
  "object_name": "InsetCube",
  "total_faces": 10,
  "face_groups": [
    {"normal": [0, 0, 1], "face_count": 2, "area": 1.2},
    {"normal": [0, 0, -1], "face_count": 1, "area": 4.0}
  ],
  "height_groups": [
    {"z_level": 0.0, "face_count": 1},
    {"z_level": 1.0, "face_count": 2}
  ],
  "detected_insets": [
    {"face_index": 5, "inset_depth": 0.1, "border_width": 0.05}
  ],
  "detected_extrusions": [
    {"face_indices": [6, 7, 8, 9], "extrusion_height": 0.3}
  ]
}
```

**Workflow:** `AFTER → deep_topology | USE FOR → inset/extrude detection`

---

### `extraction_render_angles`

**Tags:** `[OBJECT MODE][SAFE]`

Renders the object from multiple predefined angles for LLM Vision semantic analysis.

**Predefined Angles:**
| Angle | Direction | Description |
|-------|-----------|-------------|
| `front` | Y- | Front view |
| `back` | Y+ | Back view |
| `left` | X- | Left side view |
| `right` | X+ | Right side view |
| `top` | Z+ | Top-down view |
| `iso` | 45° | Isometric view (front-right-top) |

**Arguments:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `object_name` | str | required | Object to render (others hidden) |
| `angles` | list[str] | all 6 | List of angles to render |
| `resolution` | int | 512 | Image resolution in pixels |
| `output_dir` | str | /tmp/extraction_renders | Directory to save renders |

**Returns:** JSON with render paths:
```json
{
  "object_name": "Phone",
  "renders": [
    {"angle": "front", "path": "/tmp/extraction_renders/Phone_front.png"},
    {"angle": "iso", "path": "/tmp/extraction_renders/Phone_iso.png"}
  ]
}
```

**Workflow:** `AFTER → component analysis | USE FOR → LLM Vision semantic extraction`

---

## Typical Extraction Pipeline

```
1. Import/Load Model
   └── import_obj, import_fbx, import_glb

2. Component Separation (if multi-part)
   └── extraction_component_separate

3. Per-Component Analysis (parallel)
   ├── extraction_deep_topology
   ├── extraction_detect_symmetry
   ├── extraction_edge_loop_analysis
   └── extraction_face_group_analysis

4. Visual Analysis
   └── extraction_render_angles → LLM Vision

5. Workflow Generation
   └── (TASK-042 Phase 2: Pattern matching & workflow synthesis)
```

---

## Implementation Files

| Layer | File | Description |
|-------|------|-------------|
| Domain | `server/domain/tools/extraction.py` | IExtractionTool interface |
| Application | `server/application/tool_handlers/extraction_handler.py` | RPC bridge |
| Adapter | `server/adapters/mcp/areas/extraction.py` | MCP tool definitions |
| Addon | `blender_addon/application/handlers/extraction.py` | bmesh implementation |

---

## Technical Notes

### bmesh Analysis
The extraction tools use Blender's `bmesh` module for direct mesh introspection. This provides:
- O(1) access to mesh elements
- Efficient edge loop walking
- Face normal calculations
- Vertex/edge/face iteration

### KDTree Symmetry Detection
Symmetry detection uses `mathutils.kdtree` for O(log n) vertex matching:
1. Build KDTree from all vertices
2. For each vertex, query mirrored position
3. Calculate matched pair percentage as confidence

### Base Primitive Detection
The `_detect_base_primitive` method in the addon identifies:
- **CUBE**: 8 vertices, 12 edges, 6 faces (all quads)
- **PLANE**: 4 vertices, 4 edges, 1 face
- **CYLINDER**: Even vertex count on caps, parallel edge loops
- **SPHERE**: High vertex count, uniform distribution
- **CUSTOM**: Anything that doesn't match standard primitives

---

## Related Tasks

- **TASK-042**: Automatic Workflow Extraction System (parent task)
- **TASK-043**: Scene Utility Tools (dependency for viewport rendering)
- **TASK-044**: Extraction Analysis Tools (this implementation)
