# TASK-015-1: Workflow Hints dla MCP Tools

**Status:** ✅ Done
**Priority:** 🟡 Medium
**Phase:** Phase 2.1 - Advanced Selection (Enhancement)
**Created:** 2025-11-28

---

## 🎯 Cel

Dodać zwięzłe workflow hints (2-3 linie) do docstringów wszystkich 49 narzędzi MCP, aby AI lepiej rozumiało jak łączyć narzędzia w scenariusze.

---

## 📋 Format Hints

```
🔗 Workflow: BEFORE → tool_name | AFTER → tool_name | WITH → tool_name
```

---

## 📁 Pliki do modyfikacji (6)

| Plik | Narzędzia |
|------|-----------|
| `server/adapters/mcp/areas/mesh.py` | 22 |
| `server/adapters/mcp/areas/modeling.py` | 8 |
| `server/adapters/mcp/areas/scene.py` | 17 |
| `server/adapters/mcp/areas/material.py` | 2 |
| `server/adapters/mcp/areas/collection.py` | 2 |
| `server/adapters/mcp/areas/uv.py` | 1 |

**Razem:** 52 docstringi (49 narzędzi + 3 aliasy)

---

## 🔧 Workflow Hints per Tool

### MESH TOOLS (22)

| Tool | Hint |
|------|------|
| `mesh_select_all` | 🔗 Workflow: START → new workflow \| AFTER → mesh_select_by_index, mesh_select_by_location |
| `mesh_delete_selected` | 🔗 Workflow: BEFORE → mesh_select_* \| AFTER → mesh_merge_by_distance |
| `mesh_select_by_index` | 🔗 Workflow: BEFORE → mesh_get_vertex_data \| AFTER → mesh_select_linked, mesh_select_more |
| `mesh_extrude_region` | 🔗 Workflow: BEFORE → mesh_select_* \| AFTER → mesh_smooth, mesh_merge_by_distance |
| `mesh_fill_holes` | 🔗 Workflow: BEFORE → mesh_select_boundary (CRITICAL!) \| AFTER → mesh_merge_by_distance |
| `mesh_bevel` | 🔗 Workflow: BEFORE → mesh_select_loop, mesh_select_ring \| AFTER → mesh_smooth |
| `mesh_loop_cut` | 🔗 Workflow: BEFORE → mesh_select_by_index(EDGE) \| AFTER → mesh_select_loop |
| `mesh_inset` | 🔗 Workflow: BEFORE → mesh_select_*(FACE) \| AFTER → mesh_extrude_region |
| `mesh_boolean` | 🔗 Workflow: BEFORE → modeling_join_objects + mesh_select_linked \| AFTER → mesh_merge_by_distance, mesh_fill_holes |
| `mesh_merge_by_distance` | 🔗 Workflow: BEFORE → mesh_boolean, mesh_extrude \| AFTER → mesh_smooth |
| `mesh_subdivide` | 🔗 Workflow: BEFORE → mesh_select_* \| AFTER → mesh_smooth |
| `mesh_smooth` | 🔗 Workflow: BEFORE → mesh_boolean, mesh_extrude, mesh_bevel \| LAST STEP in edit workflow |
| `mesh_flatten` | 🔗 Workflow: BEFORE → mesh_select_by_location \| USE FOR → creating flat surfaces |
| `mesh_list_groups` | 🔗 Workflow: READ-ONLY \| USE WITH → scene_inspect_object |
| `mesh_select_loop` | 🔗 Workflow: BEFORE → mesh_select_by_index(EDGE) \| AFTER → mesh_bevel, mesh_extrude |
| `mesh_select_ring` | 🔗 Workflow: BEFORE → mesh_select_by_index(EDGE) \| AFTER → mesh_loop_cut |
| `mesh_select_linked` | 🔗 Workflow: BEFORE → mesh_select_by_index (one vert) \| CRITICAL FOR → mesh_boolean after join |
| `mesh_select_more` | 🔗 Workflow: AFTER → mesh_select_* \| USE → grow selection iteratively |
| `mesh_select_less` | 🔗 Workflow: AFTER → mesh_select_* \| USE → shrink selection from boundaries |
| `mesh_get_vertex_data` | 🔗 Workflow: FIRST STEP for programmatic selection \| AFTER → mesh_select_by_index, mesh_select_by_location |
| `mesh_select_by_location` | 🔗 Workflow: BEFORE → mesh_get_vertex_data (optional) \| AFTER → mesh_select_more, mesh_select_linked |
| `mesh_select_boundary` | 🔗 Workflow: CRITICAL BEFORE → mesh_fill_holes \| USE → find holes/open edges |

---

### MODELING TOOLS (8)

| Tool | Hint |
|------|------|
| `modeling_create_primitive` | 🔗 Workflow: START → new object \| AFTER → modeling_transform, scene_set_mode('EDIT') |
| `modeling_transform_object` | 🔗 Workflow: AFTER → modeling_create_primitive \| BEFORE → scene_set_mode('EDIT') |
| `modeling_add_modifier` | 🔗 Workflow: NON-DESTRUCTIVE \| AFTER → modeling_apply_modifier \| ALT TO → mesh_boolean |
| `modeling_apply_modifier` | 🔗 Workflow: BEFORE → modeling_list_modifiers \| DESTRUCTIVE - bakes changes |
| `modeling_convert_to_mesh` | 🔗 Workflow: USE FOR → Curve/Text → Mesh \| AFTER → scene_set_mode('EDIT') |
| `modeling_join_objects` | 🔗 Workflow: BEFORE → mesh_boolean workflow \| AFTER → mesh_select_linked |
| `modeling_separate_object` | 🔗 Workflow: AFTER → mesh_select_linked \| USE → split mesh islands |
| `modeling_list_modifiers` | 🔗 Workflow: READ-ONLY \| BEFORE → modeling_apply_modifier |
| `modeling_set_origin` | 🔗 Workflow: AFTER → geometry changes \| BEFORE → modeling_transform |

---

### SCENE TOOLS (17)

| Tool | Hint |
|------|------|
| `scene_list_objects` | 🔗 Workflow: READ-ONLY \| START → understand scene |
| `scene_delete_object` | 🔗 Workflow: DESTRUCTIVE \| BEFORE → scene_list_objects |
| `scene_clean_scene` | 🔗 Workflow: START → fresh scene \| AFTER → modeling_create_primitive |
| `scene_duplicate_object` | 🔗 Workflow: AFTER → scene_set_active \| USE FOR → copies with offset |
| `scene_set_active_object` | 🔗 Workflow: BEFORE → any object operation \| REQUIRED BY → modifiers, transforms |
| `scene_get_mode` | 🔗 Workflow: READ-ONLY \| USE → check context before operations |
| `scene_list_selection` | 🔗 Workflow: READ-ONLY \| USE → verify selection state |
| `scene_inspect_object` | 🔗 Workflow: READ-ONLY \| USE → detailed object audit |
| `scene_get_viewport` | 🔗 Workflow: LAST STEP → visual verification \| USE → AI preview |
| `scene_snapshot_state` | 🔗 Workflow: BEFORE → operations \| AFTER → scene_compare_snapshot |
| `scene_compare_snapshot` | 🔗 Workflow: AFTER → scene_snapshot_state (x2) \| USE → verify changes |
| `scene_inspect_material_slots` | 🔗 Workflow: READ-ONLY \| USE WITH → material_list_by_object |
| `scene_inspect_mesh_topology` | 🔗 Workflow: READ-ONLY \| USE → quality check before export |
| `scene_inspect_modifiers` | 🔗 Workflow: READ-ONLY \| BEFORE → modeling_apply_modifier |
| `scene_create_light` | 🔗 Workflow: AFTER → geometry complete \| BEFORE → scene_get_viewport |
| `scene_create_camera` | 🔗 Workflow: AFTER → geometry complete \| USE WITH → scene_get_viewport |
| `scene_create_empty` | 🔗 Workflow: USE FOR → grouping/parenting \| WITH → scene_set_active |
| `scene_set_mode` | 🔗 Workflow: CRITICAL → switching OBJECT↔EDIT \| BEFORE → mesh_* or modeling_* |

---

### MATERIAL TOOLS (2)

| Tool | Hint |
|------|------|
| `material_list` | 🔗 Workflow: READ-ONLY \| USE → find materials to assign |
| `material_list_by_object` | 🔗 Workflow: READ-ONLY \| USE WITH → scene_inspect_material_slots |

---

### COLLECTION TOOLS (2)

| Tool | Hint |
|------|------|
| `collection_list` | 🔗 Workflow: READ-ONLY \| USE → understand hierarchy |
| `collection_list_objects` | 🔗 Workflow: READ-ONLY \| USE → list collection contents |

---

### UV TOOLS (1)

| Tool | Hint |
|------|------|
| `uv_list_maps` | 🔗 Workflow: READ-ONLY \| USE → check UV setup before texturing |

---

## 📝 Przykład zmiany docstringa

### PRZED:
```python
@mcp.tool()
def mesh_fill_holes(ctx: Context) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Fills holes by creating faces.

    Args:
        None

    Returns:
        Success message.
    """
```

### PO:
```python
@mcp.tool()
def mesh_fill_holes(ctx: Context) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Fills holes by creating faces.

    🔗 Workflow: BEFORE → mesh_select_boundary (CRITICAL!) | AFTER → mesh_merge_by_distance

    Args:
        None

    Returns:
        Success message.
    """
```

---

## ✅ Deliverables

- [x] Dodać workflow hints do `mesh.py` (22 narzędzia)
- [x] Dodać workflow hints do `modeling.py` (8 narzędzi)
- [x] Dodać workflow hints do `scene.py` (17 narzędzi)
- [x] Dodać workflow hints do `material.py` (2 narzędzia)
- [x] Dodać workflow hints do `collection.py` (2 narzędzia)
- [x] Dodać workflow hints do `uv.py` (1 narzędzie)
- [x] Commit z wszystkimi zmianami

---

## 📊 Estymacja

- **Docstringi do edycji:** ~52
- **Pliki do modyfikacji:** 6
- **Commit:** 1 (docs: add workflow hints to all MCP tools)
- **Testy:** Brak (tylko dokumentacja)
