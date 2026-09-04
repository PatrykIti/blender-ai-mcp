# TASK-015-1: Mesh Select Loop Tool

**Status:** ✅ Done
**Priority:** 🟡 Medium
**Phase:** Phase 2.1 - Advanced Selection
**Completion Date:** 2025-11-28

## 🎯 Objective
Implement `mesh_select_loop` to allow AI to select edge loops (continuous lines of edges). This is crucial for selecting borders, seams, or topological rings.

## 🏗️ Architecture Requirements
### 1. Domain Layer (`server/domain/tools/mesh.py`)
- Add `select_loop(edge_index: int) -> str` to `IMeshTool`.
- Note: Loop selection typically requires a target edge to define *which* loop.

### 2. Application Layer (`server/application/tool_handlers/mesh_handler.py`)
- Implement `select_loop` delegating to RPC `mesh.select_loop`.

### 3. Adapter Layer (`server/adapters/mcp/server.py`)
- Add MCP tool `mesh_select_loop(edge_index: int) -> str`.
- Docstring: `[EDIT MODE][SELECTION-BASED][SAFE] Selects an edge loop based on the target edge index.`

### 4. Blender Addon API (`blender_addon/application/handlers/mesh.py`)
- Use `bpy.ops.mesh.loop_multi_select(ring=False)` requires context override or specific selection state.
- **Better Strategy:** Use `bmesh`.
  - Deselect all (if we want single loop) or keep existing? Usually "Select Loop" adds to selection or sets it. Let's support `add` flag?
  - `bm.edges[edge_index].select = True`
  - Then trigger `bpy.ops.mesh.loop_multi_select`? Or manually traverse `edge.link_loops`?
  - Manual traversal in BMesh is robust: find connected edges with valence 4.
  - **Simpler:** Select the target edge, then call `bpy.ops.mesh.loop_multi_select(ring=False)`.
  - Ensure correct context (Edit Mode).

### 5. Registration
- Register `mesh.select_loop` in `blender_addon/__init__.py`.

## ✅ Deliverables
- Implementation in all layers.
- Tests in `tests/test_mesh_selection_advanced.py`.
- Documentation update in `_docs/MESH_TOOLS_ARCHITECTURE.md`.

---

# TASK-015-2: Mesh Select Ring Tool

**Status:** ✅ Done
**Priority:** 🟡 Medium
**Phase:** Phase 2.1 - Advanced Selection
**Completion Date:** 2025-11-28

## 🎯 Objective
Implement `mesh_select_ring` to select parallel rings of edges.

## 🏗️ Architecture Requirements
### 1. Domain Layer
- Add `select_ring(edge_index: int) -> str` to `IMeshTool`.

### 2. Application Layer
- Implement `select_ring`.

### 3. Adapter Layer
- Add `mesh_select_ring(edge_index: int)`.
- Docstring: `[EDIT MODE][SELECTION-BASED][SAFE] Selects an edge ring based on target edge.`

### 4. Blender Addon API
- Similar to Loop, but `bpy.ops.mesh.loop_multi_select(ring=True)`.
- Or use BMesh traversal.

### 5. Registration
- Register `mesh.select_ring`.

## ✅ Deliverables
- Implementation + Tests.
- Docs update.

---

# TASK-015-3: Mesh Select Linked Tool

**Status:** ✅ Done
**Priority:** 🟡 Medium
**Phase:** Phase 2.1 - Advanced Selection
**Completion Date:** 2025-11-28

## 🎯 Objective
Implement `mesh_select_linked` to select all geometry connected to the currently selected elements (Islands).

## 🏗️ Architecture Requirements
### 1. Domain Layer
- Add `select_linked() -> str` to `IMeshTool`.

### 2. Application Layer
- Implement `select_linked`.

### 3. Adapter Layer
- Add `mesh_select_linked()`.
- Docstring: `[EDIT MODE][SELECTION-BASED][SAFE] Selects all geometry linked to current selection.`

### 4. Blender Addon API
- `bpy.ops.mesh.select_linked()`.

### 5. Registration
- Register `mesh.select_linked`.

## ✅ Deliverables
- Implementation + Tests.
- Docs update.

---

# TASK-015-4: Mesh Select More/Less Tools

**Status:** ✅ Done
**Priority:** 🟡 Medium
**Phase:** Phase 2.1 - Advanced Selection
**Completion Date:** 2025-11-28

## 🎯 Objective
Implement tools to grow (`select_more`) or shrink (`select_less`) the current selection.

## 🏗️ Architecture Requirements
### 1. Domain Layer
- Add `select_more() -> str` and `select_less() -> str`.

### 2. Application Layer
- Implement both methods.

### 3. Adapter Layer
- Add `mesh_select_more()` and `mesh_select_less()`.
- Docstrings: `[EDIT MODE][SELECTION-BASED][SAFE] ...`

### 4. Blender Addon API
- `bpy.ops.mesh.select_more()`
- `bpy.ops.mesh.select_less()`

### 5. Registration
- Register both endpoints.

## ✅ Deliverables
- Implementation + Tests.
- Docs update.

---

# TASK-015-5: Mesh Get Vertex Data Tool

**Status:** ✅ Done
**Priority:** 🔴 High (Required for programmatic selection)
**Phase:** Phase 2.1 - Advanced Selection
**Completion Date:** 2025-11-28

## 🎯 Objective
Implement `mesh_get_vertex_data` to read vertex positions and selection states. This is a **READ-ONLY introspection tool** that enables AI to make programmatic selection decisions based on geometry data.

## 🏗️ Architecture Requirements
### 1. Domain Layer
- Add `get_vertex_data(object_name: str, selected_only: bool = False) -> dict` to `IMeshTool`.
- Returns structured data with vertex indices, positions, and selection states.

### 2. Application Layer
- Implement `get_vertex_data` delegating to RPC `mesh.get_vertex_data`.

### 3. Adapter Layer
- Add `mesh_get_vertex_data(object_name: str, selected_only: bool = False) -> str`.
- Docstring: `[EDIT MODE][READ-ONLY][SAFE] Returns vertex positions and selection states for programmatic analysis.`
- Returns JSON string with:
  ```json
  {
    "vertex_count": 8,
    "selected_count": 4,
    "vertices": [
      {"index": 0, "position": [1.0, 1.0, 1.0], "selected": true},
      {"index": 1, "position": [1.0, -1.0, 1.0], "selected": false}
    ]
  }
  ```

### 4. Blender Addon API
- Use `bmesh` to read vertex data:
  ```python
  bm = bmesh.from_edit_mesh(obj.data)
  vertices = []
  for v in bm.verts:
      if selected_only and not v.select:
          continue
      vertices.append({
          "index": v.index,
          "position": [v.co.x, v.co.y, v.co.z],
          "selected": v.select
      })
  ```
- No mesh modification - pure read operation.

### 5. Registration
- Register `mesh.get_vertex_data` in `blender_addon/__init__.py`.

## ✅ Deliverables
- Implementation in all layers.
- Tests in `tests/test_mesh_introspection.py`.
- Documentation update in `_docs/MESH_TOOLS_ARCHITECTURE.md`.

## 📊 Use Cases
- AI can analyze vertex positions to determine selection strategy
- Enables `mesh_select_by_location` to validate coordinate ranges
- Allows AI to understand geometry before performing operations

---

# TASK-015-6: Mesh Select By Location Tool

**Status:** ✅ Done
**Priority:** 🟡 Medium (Depends on TASK-015-5)
**Phase:** Phase 2.1 - Advanced Selection
**Completion Date:** 2025-11-28

## 🎯 Objective
Implement `mesh_select_by_location` to select vertices/edges/faces based on coordinate ranges. This enables spatial selection without manual index specification.

## 🏗️ Architecture Requirements
### 1. Domain Layer
- Add `select_by_location(axis: str, min: float, max: float, mode: str = 'VERT') -> str` to `IMeshTool`.
- `axis`: 'X', 'Y', 'Z'
- `min`/`max`: Coordinate range
- `mode`: 'VERT', 'EDGE', 'FACE'

### 2. Application Layer
- Implement `select_by_location` delegating to RPC.

### 3. Adapter Layer
- Add `mesh_select_by_location(axis: str, min: float, max: float, mode: str = 'VERT')`.
- Docstring: `[EDIT MODE][SELECTION-BASED][SAFE] Selects geometry within coordinate range. Example: axis='Z', min=0.5, max=2.0 selects all vertices above Z=0.5.`

### 4. Blender Addon API
- Use `bmesh` to iterate and select:
  ```python
  bm = bmesh.from_edit_mesh(obj.data)
  axis_idx = {'X': 0, 'Y': 1, 'Z': 2}[axis]

  if mode == 'VERT':
      for v in bm.verts:
          if min <= v.co[axis_idx] <= max:
              v.select = True
  # Similar for EDGE (check both verts) and FACE (check centroid)

  bmesh.update_edit_mesh(obj.data)
  ```

### 5. Registration
- Register `mesh.select_by_location`.

## ✅ Deliverables
- Implementation + Tests.
- Docs update.

## 📊 Use Cases
- "Select all vertices above Z=0.5" (top half of object)
- "Select faces in the middle section (Y between -0.5 and 0.5)"
- Enables spatial operations without knowing exact vertex indices

---

# TASK-015-7: Mesh Select Boundary Tool

**Status:** ✅ Done
**Priority:** 🔴 Critical (Required for mesh_fill_holes)
**Phase:** Phase 2.1 - Advanced Selection
**Completion Date:** 2025-11-28

## 🎯 Objective
Implement `mesh_select_boundary` to select boundary edges (edges with only one adjacent face) and boundary vertices. This is **CRITICAL** for `mesh_fill_holes` to target specific holes.

## 🏗️ Architecture Requirements
### 1. Domain Layer
- Add `select_boundary(mode: str = 'EDGE') -> str` to `IMeshTool`.
- `mode`: 'EDGE' (edges with 1 face) or 'VERT' (vertices on boundary)

### 2. Application Layer
- Implement `select_boundary` delegating to RPC.

### 3. Adapter Layer
- Add `mesh_select_boundary(mode: str = 'EDGE')`.
- Docstring: `[EDIT MODE][SELECTION-BASED][SAFE] Selects boundary edges (1 adjacent face) or boundary vertices. CRITICAL for mesh_fill_holes - use this to select hole edges before filling.`

### 4. Blender Addon API
- Use `bmesh` to find boundary:
  ```python
  bm = bmesh.from_edit_mesh(obj.data)

  if mode == 'EDGE':
      for edge in bm.edges:
          if edge.is_boundary:  # Only 1 adjacent face
              edge.select = True

  elif mode == 'VERT':
      for vert in bm.verts:
          if vert.is_boundary:
              vert.select = True

  bmesh.update_edit_mesh(obj.data)
  ```
- Alternative: Use `bpy.ops.mesh.region_to_loop()` to convert face selection to boundary.

### 5. Registration
- Register `mesh.select_boundary`.

## ✅ Deliverables
- Implementation + Tests.
- Docs update.

## 📊 Use Cases
- **Primary:** Select hole edges before `mesh_fill_holes` (instead of selecting everything)
- Identify open edges in mesh for quality checks
- Select boundary loops for extrusion/detachment operations

## 🔗 Dependencies
- **Blocks:** `mesh_fill_holes` reliable operation
- **Required by:** Any workflow involving filling specific holes

---

## 📋 Phase 2.1 Summary

**Total Tasks:** 7
**Priority Breakdown:**
- 🔴 Critical: 2 (mesh_get_vertex_data, mesh_select_boundary)
- 🟡 Medium: 5 (others)

**Dependencies:**
1. **TASK-015-5** (mesh_get_vertex_data) should be implemented first - enables inspection for all other tools
2. **TASK-015-7** (mesh_select_boundary) is critical for mesh_fill_holes workflow
3. **TASK-015-3** (mesh_select_linked) is critical for mesh_boolean after join_objects
4. Others can be implemented in parallel
