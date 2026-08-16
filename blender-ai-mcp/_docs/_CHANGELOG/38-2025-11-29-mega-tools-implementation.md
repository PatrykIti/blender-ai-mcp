# Changelog: Mega Tools Implementation (TASK-020)

**Date:** 2025-11-29
**Type:** Feature / LLM Context Optimization
**Tasks:** TASK-020-1, TASK-020-2, TASK-020-3, TASK-020-4, TASK-020-5

---

## Summary

Implemented 5 "mega tools" that consolidate 18 related operations into unified tools with action parameters.
This reduces LLM context usage by **-13 tool definitions**.

---

## Changes

### New Mega Tools

| Tool | Actions | Replaces |
|------|---------|----------|
| `scene_context` | `mode`, `selection` | `scene_get_mode`, `scene_list_selection` |
| `scene_create` | `light`, `camera`, `empty` | `scene_create_light`, `scene_create_camera`, `scene_create_empty` |
| `scene_inspect` | `object`, `topology`, `modifiers`, `materials` | `scene_inspect_object`, `scene_inspect_mesh_topology`, `scene_inspect_modifiers`, `scene_inspect_material_slots` |
| `mesh_select` | `all`, `none`, `linked`, `more`, `less`, `boundary` | `mesh_select_all`, `mesh_select_linked`, `mesh_select_more`, `mesh_select_less`, `mesh_select_boundary` |
| `mesh_select_targeted` | `by_index`, `loop`, `ring`, `by_location` | `mesh_select_by_index`, `mesh_select_loop`, `mesh_select_ring`, `mesh_select_by_location` |

### Implementation Details

- Original functions converted to internal functions (prefixed with `_`)
- Mega tools route to internal functions based on `action` parameter
- Parameter validation with helpful error messages
- Full backward compatibility maintained

---

## Files Changed

### Modified
- `server/adapters/mcp/areas/scene.py` - Added `scene_context`, `scene_create`, `scene_inspect`; converted 9 functions to internal
- `server/adapters/mcp/areas/mesh.py` - Added `mesh_select`, `mesh_select_targeted`; converted 9 functions to internal

### New Documentation
- `_docs/MEGA_TOOLS_ARCHITECTURE.md` - Complete mega tools specification
- `_docs/_CHANGELOG/38-2025-11-29-mega-tools-implementation.md` - This changelog

### Updated Documentation
- `_docs/AVAILABLE_TOOLS_SUMMARY.md` - Added mega tools section, marked deprecated tools
- `_docs/SCENE_TOOLS_ARCHITECTURE.md` - Added reference to mega tools
- `README.md` - Updated LLM Context Optimization section

---

## Testing

All 127 tests pass (19 skipped - require running Blender).

---

## Usage Examples

### scene_context
```python
# Get current mode
scene_context(action="mode")

# Get selection state
scene_context(action="selection")
```

### scene_create
```python
# Create a sun light
scene_create(action="light", light_type="SUN", energy=5.0)

# Create a camera
scene_create(action="camera", location=[0, -10, 5], rotation=[1.0, 0, 0])

# Create an empty
scene_create(action="empty", empty_type="ARROWS")
```

### mesh_select
```python
# Select all
mesh_select(action="all")

# Deselect all
mesh_select(action="none")

# Select linked geometry
mesh_select(action="linked")

# Select boundary edges
mesh_select(action="boundary", boundary_mode="EDGE")
```

### mesh_select_targeted
```python
# Select by index
mesh_select_targeted(action="by_index", indices=[0, 1, 2], element_type="VERT")

# Select edge loop
mesh_select_targeted(action="loop", edge_index=4)

# Select by location
mesh_select_targeted(action="by_location", axis="Z", min_coord=0.5, max_coord=2.0)
```
