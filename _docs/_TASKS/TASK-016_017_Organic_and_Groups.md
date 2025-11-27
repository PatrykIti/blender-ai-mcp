# TASK-016-1: Mesh Randomize Tool

**Status:** ⏳ To Do  
**Priority:** 🟡 Medium  
**Phase:** Phase 2.2 - Organic & Deform

## 🎯 Objective
Implement `mesh_randomize` to displace vertices randomly. Useful for making organic surfaces less perfect.

## 🏗️ Architecture Requirements
### 1. Domain Layer (`server/domain/tools/mesh.py`)
- Add `randomize(amount: float = 0.1, uniform: float = 0.0, normal: float = 0.0, seed: int = 0) -> str`.

### 2. Application Layer
- Implement `randomize`.

### 3. Adapter Layer
- Add `mesh_randomize(amount: float = 0.1, ...)`
- Docstring: `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Randomizes vertex positions.`

### 4. Blender Addon API
- `bpy.ops.transform.vertex_random(...)`.

### 5. Registration
- Register `mesh.randomize`.

## ✅ Deliverables
- Implementation + Tests.
- Docs update.

---

# TASK-016-2: Mesh Shrink/Fatten Tool

**Status:** ⏳ To Do  
**Priority:** 🟡 Medium  
**Phase:** Phase 2.2 - Organic & Deform

## 🎯 Objective
Implement `mesh_shrink_fatten` to move vertices along their normals. Crucial for thickening or thinning organic shapes without losing volume style.

## 🏗️ Architecture Requirements
### 1. Domain Layer
- Add `shrink_fatten(value: float) -> str`.

### 2. Application Layer
- Implement `shrink_fatten`.

### 3. Adapter Layer
- Add `mesh_shrink_fatten(value: float)`.
- Docstring: `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Moves vertices along their normals (Shrink/Fatten).`

### 4. Blender Addon API
- `bpy.ops.transform.shrink_fatten(value=value)`.

### 5. Registration
- Register `mesh.shrink_fatten`.

## ✅ Deliverables
- Implementation + Tests.
- Docs update.

---

# TASK-017-1: Mesh Create Vertex Group Tool

**Status:** ⏳ To Do  
**Priority:** 🟡 Medium  
**Phase:** Phase 2.3 - Vertex Groups

## 🎯 Objective
Allow AI to create named vertex groups.

## 🏗️ Architecture Requirements
### 1. Domain Layer
- Add `create_vertex_group(object_name: str, name: str) -> str`.

### 2. Application Layer
- Implement. Note: This could be `modeling_` or `mesh_`. Usually vertex groups are object data but manipulated in Edit/Object mode. Let's keep in `mesh_` or `modeling_`? `mesh_list_groups` is `mesh_`. Let's stick to `mesh_` for consistency with vertex ops.

### 3. Adapter Layer
- Add `mesh_create_vertex_group(object_name: str, name: str)`.
- Docstring: `[MESH][SAFE] Creates a new vertex group.`

### 4. Blender Addon API
- `obj.vertex_groups.new(name=name)`.

### 5. Registration
- Register.

## ✅ Deliverables
- Implementation + Tests.
- Docs update.

---

# TASK-017-2: Mesh Assign/Remove Vertex Group Tools

**Status:** ⏳ To Do  
**Priority:** 🟡 Medium  
**Phase:** Phase 2.3 - Vertex Groups

## 🎯 Objective
Assign or remove selected vertices to/from a vertex group.

## 🏗️ Architecture Requirements
### 1. Domain Layer
- `assign_to_group(object_name: str, group_name: str, weight: float = 1.0) -> str`.
- `remove_from_group(object_name: str, group_name: str) -> str`.

### 2. Application Layer
- Implement both.

### 3. Adapter Layer
- `mesh_assign_to_group(...)`.
- `mesh_remove_from_group(...)`.
- Docstrings: `[EDIT MODE][SELECTION-BASED][SAFE] ...`

### 4. Blender Addon API
- `bpy.ops.object.vertex_group_assign()` / `remove()`.
- Or `vg.add([v.index for v in selected], weight, 'REPLACE')` via API (safer than ops if we can get selection easily).
- Ideally use `bpy.ops` for consistency with "Edit Mode Selection".

### 5. Registration
- Register endpoints.

## ✅ Deliverables
- Implementation + Tests.
- Docs update.
