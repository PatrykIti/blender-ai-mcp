title: Edge Operations (Bevel, Loop Cut, Inset)
status: done
priority: medium
assignee: unassigned
depends_on: TASK-011-2
---

# 🎯 Objective
Implement tools for adding detail and controlling topology.

## 📋 Requirements

### 1. Interface (`IMeshTool`)
*   Add methods:
    *   `bevel(offset: float, segments: int, profile: float = 0.5, affect: str = 'EDGES') -> str`
    *   `loop_cut(number_cuts: int, smoothness: float = 0.0) -> str`
    *   `inset(thickness: float, depth: float = 0.0) -> str`

### 2. Implementation
*   **Bevel:** `bpy.ops.mesh.bevel`. Note: requires selecting edges first.
*   **Loop Cut:** `bpy.ops.mesh.loopcut_slide`. *Note:* Loop cut is tricky via API because it depends on the "last selected edge". AI might struggle to "aim" it. We might need a way to select edge rings. For MVP, rely on `bpy.ops` default behavior on selected edges.
*   **Inset:** `bpy.ops.mesh.inset`.

## ✅ Checklist
- [x] Update `IMeshTool` & `MeshToolHandler`.
- [x] Update Addon `MeshHandler`.
- [x] Register `mesh_bevel`, `mesh_loop_cut`, `mesh_inset`.
- [x] Tests.
