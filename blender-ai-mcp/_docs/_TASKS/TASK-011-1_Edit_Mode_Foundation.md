# TASK-011-1: Edit Mode Foundation (Selection & Deletion)

## 🎯 Objective
Establish the foundation for **Edit Mode** operations. Unlike Object Mode tools, these tools must operate on the mesh geometry (vertices, edges, faces). This requires managing mode switching (Object <-> Edit) and using the `bmesh` module.

## 📋 Requirements

### 1. Domain Layer
*   Create `server/domain/tools/mesh.py` with `IMeshTool` interface.
*   Define methods:
    *   `select_all(deselect: bool = False) -> str`
    *   `delete_selected(type: str = 'VERT') -> str` (VERT, EDGE, FACE)
    *   `select_by_index(indices: List[int], type: str = 'VERT', deselect: bool = False) -> str`

### 2. Server Application Layer
*   Create `server/application/tool_handlers/mesh_handler.py`.
*   Implement `MeshToolHandler`.

### 3. Blender Addon Implementation
*   Create `blender_addon/application/handlers/mesh.py`.
*   **Logic:**
    1.  Ensure active object is a MESH.
    2.  Switch to Edit Mode (`bpy.ops.object.mode_set(mode='EDIT')`).
    3.  Use `bmesh.from_edit_mesh(bpy.context.edit_object.data)` for advanced selection logic (by index).
    4.  For simple ops, `bpy.ops.mesh` might suffice, but `bmesh` is safer for precise indexing.
    5.  **Important:** `bmesh.update_edit_mesh()` must be called to refresh the view.

### 4. Adapter Layer
*   Register `MeshToolHandler` in DI container.
*   Expose tools in `server/adapters/mcp/server.py` with prefix `mesh_`.

## ✅ Checklist
- [ ] Create `IMeshTool` interface.
- [ ] Create `MeshToolHandler`.
- [ ] Implement `MeshHandler` in Addon (handling Object/Edit mode switch).
- [ ] Register tools: `mesh_select_all`, `mesh_delete_selected`, `mesh_select_by_index`.
- [ ] Add tests for Mesh tools.
