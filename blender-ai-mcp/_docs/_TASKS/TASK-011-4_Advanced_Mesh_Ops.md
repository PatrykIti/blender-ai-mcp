# TASK-011-4: Advanced Mesh Ops (Boolean, Merge, Subdivide)

## 🎯 Objective
Tools for boolean logic, cleaning up topology, and increasing density.

## 📋 Requirements

### 1. Interface (`IMeshTool`)
*   Add methods:
    *   `boolean(operation: str, target_object: str) -> str` (INTERSECT, UNION, DIFFERENCE). *Note: This might be a Modifier wrapper or Edit Mode boolean.* Edit Mode boolean is `bpy.ops.mesh.intersect_boolean`.
    *   `merge_by_distance(distance: float) -> str` (Cleanup).
    *   `subdivide(number_cuts: int, smoothness: float = 0.0) -> str`.

### 2. Implementation
*   **Boolean:** Since we have `modeling_add_modifier` for non-destructive booleans, this tool should perhaps be `mesh_boolean_edit` or we rely on modifiers. Let's implement **Edit Mode Boolean** (`bpy.ops.mesh.intersect_boolean`) which is immediate.
*   **Merge:** `bpy.ops.mesh.remove_doubles`.
*   **Subdivide:** `bpy.ops.mesh.subdivide`.

## ✅ Checklist
- [ ] Update `IMeshTool` & `MeshToolHandler`.
- [ ] Update Addon `MeshHandler`.
- [ ] Register tools.
- [ ] Tests.
