title: Basic Extrusions & Face Operations
status: done
priority: high
assignee: unassigned
depends_on: TASK-011-1
---

# 🎯 Objective
Implement the most fundamental modeling operations: Extruding geometry and filling holes. These tools allow the AI to grow the mesh.

## 📋 Requirements

### 1. Interface (`IMeshTool`)
*   Add methods:
    *   `extrude_region(mode: str = 'REGION', move: List[float] = None) -> str`
    *   `fill_holes() -> str`

### 2. Implementation
*   **Extrude:**
    *   Use `bpy.ops.mesh.extrude_region_move`.
    *   Support optional translation vector after extrusion.
*   **Fill:**
    *   Use `bpy.ops.mesh.fill()` or `bpy.ops.mesh.edge_face_add()`.

## ✅ Checklist
- [x] Update `IMeshTool` & `MeshToolHandler`.
- [x] Update Addon `MeshHandler`.
- [x] Register `mesh_extrude_region`, `mesh_fill_holes`.
- [x] Tests.

