# TASK-018-1: Mesh Bisect Tool

**Status:** ✅ Done
**Priority:** 🟡 Medium
**Phase:** Phase 2.5 - Advanced Precision

## 🎯 Objective
Implement `mesh_bisect` to cut the mesh in half or along a plane.

## 🏗️ Architecture Requirements
### 1. Domain Layer
- `bisect(plane_co: List[float], plane_no: List[float], clear_inner: bool = False, clear_outer: bool = False, fill: bool = False) -> str`.

### 2. Application Layer
- Implement.

### 3. Adapter Layer
- `mesh_bisect(...)`.
- Docstring: `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Cuts mesh along a plane.`

### 4. Blender Addon API
- `bpy.ops.mesh.bisect(...)`.

### 5. Registration
- Register.

## ✅ Deliverables
- Implementation + Tests.
- Docs update.

---

# TASK-018-2: Mesh Edge/Vertex Slide Tools

**Status:** ✅ Done
**Priority:** 🟡 Medium
**Phase:** Phase 2.5 - Advanced Precision

## 🎯 Objective
Implement tools to slide edges or vertices along existing topology.

## 🏗️ Architecture Requirements
### 1. Domain Layer
- `edge_slide(value: float = 0.0) -> str`.
- `vert_slide(value: float = 0.0) -> str`.

### 2. Application Layer
- Implement both.

### 3. Adapter Layer
- `mesh_edge_slide(...)`
- `mesh_vert_slide(...)`

### 4. Blender Addon API
- `bpy.ops.transform.edge_slide(value=value)`.
- `bpy.ops.transform.vert_slide(value=value)`.

### 5. Registration
- Register.

## ✅ Deliverables
- Implementation + Tests.
- Docs update.

---

# TASK-018-3: Mesh Triangulate Tool

**Status:** ✅ Done
**Priority:** 🟢 Low
**Phase:** Phase 2.5 - Advanced Precision

## 🎯 Objective
Convert selected faces to triangles.

## 🏗️ Architecture Requirements
### 1. Domain Layer
- `triangulate() -> str`.

### 2. Application Layer
- Implement.

### 3. Adapter Layer
- `mesh_triangulate()`.

### 4. Blender Addon API
- `bpy.ops.mesh.quads_convert_to_tris()`.

### 5. Registration
- Register.

## ✅ Deliverables
- Implementation + Tests.
- Docs update.

---

# TASK-018-4: Mesh Remesh Voxel Tool

**Status:** ✅ Done
**Priority:** 🟡 Medium
**Phase:** Phase 2.5 - Advanced Precision

## 🎯 Objective
Perform a voxel remesh on the object. This is typically an **Object Mode** destructive operation, but it fundamentally alters the mesh. It usually fits `mesh_` prefix if we consider it a mesh generation tool, or `modeling_`. Given it's a "Remesh" modifier alternative, `mesh_remesh_voxel` is fine.

## 🏗️ Architecture Requirements
### 1. Domain Layer
- `remesh_voxel(voxel_size: float = 0.1, adaptivity: float = 0.0) -> str`.

### 2. Application Layer
- Implement.

### 3. Adapter Layer
- `mesh_remesh_voxel(...)`.
- Docstring: `[OBJECT MODE][DESTRUCTIVE] Remeshes object using Voxel algorithm.` (Tag appropriately as Object Mode!).

### 4. Blender Addon API
- `bpy.ops.object.voxel_remesh()`.
- Requires setting `obj.data.remesh_voxel_size` first.

### 5. Registration
- Register.

## ✅ Deliverables
- Implementation + Tests.
- Docs update.
