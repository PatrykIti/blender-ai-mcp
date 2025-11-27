# TASK-015-1: Mesh Select Loop Tool

**Status:** ⏳ To Do  
**Priority:** 🟡 Medium  
**Phase:** Phase 2.1 - Advanced Selection

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

**Status:** ⏳ To Do  
**Priority:** 🟡 Medium  
**Phase:** Phase 2.1 - Advanced Selection

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

**Status:** ⏳ To Do  
**Priority:** 🟡 Medium  
**Phase:** Phase 2.1 - Advanced Selection

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

**Status:** ⏳ To Do  
**Priority:** 🟡 Medium  
**Phase:** Phase 2.1 - Advanced Selection

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
