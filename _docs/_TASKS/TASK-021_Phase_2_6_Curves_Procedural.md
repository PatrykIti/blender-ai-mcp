# TASK-021-1: Curve Create Tool

**Status:** ✅ Done
**Priority:** 🟡 Medium
**Phase:** Phase 2.6 - Curves & Procedural

## 🎯 Objective
Implement `curve_create` to create various curve primitives (Bezier, NURBS, Path).

## 🏗️ Architecture Requirements
### 1. Domain Layer
- `create_curve(curve_type: str = 'BEZIER', location: List[float] = None) -> str`.
- Types: BEZIER, NURBS, PATH, CIRCLE.

### 2. Application Layer
- Implement RPC bridge.

### 3. Adapter Layer
- `curve_create(...)`.
- Docstring: `[OBJECT MODE][SAFE] Creates a curve primitive.`

### 4. Blender Addon API
- `bpy.ops.curve.primitive_bezier_curve_add(...)`.
- `bpy.ops.curve.primitive_nurbs_curve_add(...)`.
- `bpy.ops.curve.primitive_nurbs_path_add(...)`.
- `bpy.ops.curve.primitive_bezier_circle_add(...)`.

### 5. Registration
- Register handler.

## ✅ Deliverables
- Implementation + Tests.
- Docs update.

---

# TASK-021-2: Curve To Mesh Tool

**Status:** ✅ Done
**Priority:** 🟡 Medium
**Phase:** Phase 2.6 - Curves & Procedural

## 🎯 Objective
Implement `curve_to_mesh` to convert a curve object to mesh geometry.

## 🏗️ Architecture Requirements
### 1. Domain Layer
- `curve_to_mesh(object_name: str) -> str`.

### 2. Application Layer
- Implement RPC bridge.

### 3. Adapter Layer
- `curve_to_mesh(...)`.
- Docstring: `[OBJECT MODE][DESTRUCTIVE] Converts curve to mesh.`

### 4. Blender Addon API
- `bpy.ops.object.convert(target='MESH')`.
- Or use existing `modeling_convert_to_mesh` if it handles curves.

### 5. Registration
- Register handler (or extend existing convert tool).

## ✅ Deliverables
- Implementation + Tests.
- Docs update.

---

# TASK-021-3: Mesh Spin Tool

**Status:** ✅ Done
**Priority:** 🟡 Medium
**Phase:** Phase 2.6 - Curves & Procedural

## 🎯 Objective
Implement `mesh_spin` to spin/lathe selected geometry around an axis.

## 🏗️ Architecture Requirements
### 1. Domain Layer
- `spin(steps: int = 12, angle: float = 6.283185, axis: str = 'Z', center: List[float] = None, dupli: bool = False) -> str`.

### 2. Application Layer
- Implement RPC bridge.

### 3. Adapter Layer
- `mesh_spin(...)`.
- Docstring: `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Spins geometry around axis (lathe).`

### 4. Blender Addon API
- `bpy.ops.mesh.spin(steps=..., angle=..., axis=..., center=..., dupli=...)`.

### 5. Registration
- Register handler.

## ✅ Deliverables
- Implementation + Tests.
- Docs update.

---

# TASK-021-4: Mesh Screw Tool

**Status:** ✅ Done
**Priority:** 🟡 Medium
**Phase:** Phase 2.6 - Curves & Procedural

## 🎯 Objective
Implement `mesh_screw` to create helical/spiral geometry from selected profile.

## 🏗️ Architecture Requirements
### 1. Domain Layer
- `screw(steps: int = 12, turns: int = 1, axis: str = 'Z', center: List[float] = None, offset: float = 0.0) -> str`.

### 2. Application Layer
- Implement RPC bridge.

### 3. Adapter Layer
- `mesh_screw(...)`.
- Docstring: `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Creates spiral/screw geometry.`

### 4. Blender Addon API
- `bpy.ops.mesh.screw(...)`.

### 5. Registration
- Register handler.

## ✅ Deliverables
- Implementation + Tests.
- Docs update.

---

# TASK-021-5: Mesh Add Geometry Tools

**Status:** ✅ Done
**Priority:** 🟢 Low
**Phase:** Phase 2.6 - Curves & Procedural

## 🎯 Objective
Implement primitive geometry creation tools for Edit Mode:
- `mesh_add_vertex` - Add single vertex at position.
- `mesh_add_edge` - Add edge between two selected vertices.
- `mesh_add_face` - Add face from selected vertices/edges.

## 🏗️ Architecture Requirements
### 1. Domain Layer
- `add_vertex(position: List[float]) -> str`.
- `add_edge() -> str` (operates on 2 selected verts).
- `add_face() -> str` (operates on 3+ selected verts).

### 2. Application Layer
- Implement RPC bridges.

### 3. Adapter Layer
- `mesh_add_vertex(...)`.
- `mesh_add_edge()`.
- `mesh_add_face()`.
- Docstrings: `[EDIT MODE][DESTRUCTIVE]`.

### 4. Blender Addon API
- BMesh: `bm.verts.new(co)`.
- BMesh: `bm.edges.new([v1, v2])`.
- BMesh: `bm.faces.new([v1, v2, v3, ...])`.
- Or: `bpy.ops.mesh.edge_face_add()` for face/edge.

### 5. Registration
- Register handlers.

## ✅ Deliverables
- Implementation + Tests.
- Docs update.
