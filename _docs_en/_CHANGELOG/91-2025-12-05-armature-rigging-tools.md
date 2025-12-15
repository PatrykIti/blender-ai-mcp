# 91 - Armature & Rigging Tools (TASK-037)

**Date:** 2025-12-05
**Version:** 1.31.0
**Task:** [TASK-037](../_TASKS/TASK-037_Armature_Rigging.md)

---

## Summary

Implemented complete armature and rigging toolset enabling skeletal animation capabilities. This includes armature creation, bone management, mesh binding with automatic weights, pose manipulation, and weight painting.

---

## New Tools (5)

### Armature Tools (`armature_*`)

| Tool | Description | Mode |
|------|-------------|------|
| `armature_create` | Creates armature with initial bone | OBJECT |
| `armature_add_bone` | Adds bone to existing armature with optional parenting | EDIT (armature) |
| `armature_bind` | Binds mesh to armature with AUTO/ENVELOPE/EMPTY weights | OBJECT |
| `armature_pose_bone` | Poses bone (rotation/location/scale) | POSE |
| `armature_weight_paint_assign` | Assigns weights to selected vertices | EDIT/WEIGHT_PAINT |

---

## Architecture

### Files Created

| Layer | File |
|-------|------|
| Domain | `server/domain/tools/armature.py` |
| Application | `server/application/tool_handlers/armature_handler.py` |
| Adapter | `server/adapters/mcp/areas/armature.py` |
| Addon | `blender_addon/application/handlers/armature.py` |

### Infrastructure Updates

| File | Change |
|------|--------|
| `blender_addon/__init__.py` | Added handler instantiation and 5 RPC registrations |
| `server/infrastructure/di.py` | Added `get_armature_handler()` |
| `server/adapters/mcp/dispatcher.py` | Added armature tool mappings |
| `server/router/infrastructure/tools_metadata/_schema.json` | Added "armature" category and "POSE" mode |

### Router Metadata

Created 5 JSON files in `server/router/infrastructure/tools_metadata/armature/`:
- `armature_create.json`
- `armature_add_bone.json`
- `armature_bind.json`
- `armature_pose_bone.json`
- `armature_weight_paint_assign.json`

---

## Testing

| Type | Count | Status |
|------|-------|--------|
| Unit Tests | 34 | ✅ Passing |
| E2E Tests | 18 | ✅ Passing |

### Test Coverage

- Armature creation with custom name, location, bone name, bone length
- Bone addition with head/tail positions, parenting, connected bones
- Mesh binding with all bind types (AUTO, ENVELOPE, EMPTY)
- Bone posing with rotation, location, scale
- Weight assignment with REPLACE, ADD, SUBTRACT modes
- Error handling for missing objects, invalid parameters
- Complete workflow tests (simple rig, arm rig)

---

## Use Cases

- **Character rigging** for games/film
- **Mechanical rigs** (robot arms, machines)
- **Procedural animation** setups
- **Weight painting** for precise deformation control

---

## Example Usage

```python
# Create armature
armature_create(name="CharacterRig", bone_name="Root", bone_length=1.0)

# Add bone hierarchy
armature_add_bone(armature_name="CharacterRig", bone_name="Spine",
                  head=[0, 0, 0], tail=[0, 0, 1], parent_bone="Root", use_connect=True)

# Bind mesh to armature
armature_bind(mesh_name="Character", armature_name="CharacterRig", bind_type="AUTO")

# Pose bone
armature_pose_bone(armature_name="CharacterRig", bone_name="Spine",
                   rotation=[15, 0, 0])

# Manual weight assignment
armature_weight_paint_assign(object_name="Character", vertex_group="Spine",
                             weight=1.0, mode="REPLACE")
```

---

## Breaking Changes

None.

---

## Dependencies

- TASK-017 (Vertex Groups) - Required for weight painting functionality
