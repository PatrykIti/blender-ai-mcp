# TASK-082: Animation and Driver Tools (Inspect + Build)

**Priority:** 🟡 Medium  
**Category:** Animation Reconstruction  
**Estimated Effort:** Large  
**Dependencies:** TASK-037, TASK-045  
**Status:** ⬜ To Do

---

## 🎯 Objective

Add tools to inspect and rebuild animation data (actions, FCurves, NLA, drivers).

This is required for 1:1 reconstruction of animated objects and rigs.

---

## 📝 Documentation Updates

| File | What to Update |
|------|----------------|
| `_docs/_TASKS/TASK-082_Animation_and_Drivers_Tools.md` | Track status and sub-tasks |
| `_docs/_TASKS/README.md` | Add to task list + stats |
| `_docs/_MCP_SERVER/README.md` | Add animation tools |
| `_docs/AVAILABLE_TOOLS_SUMMARY.md` | Add animation tools |
| `_docs/TOOLS/MEGA_TOOLS_ARCHITECTURE.md` | Document new mega tools |
| `_docs/TOOLS/SCENE_TOOLS_ARCHITECTURE.md` | Add animation/driver sections |
| `README.md` | Update tools tables |

---

## 🔧 Design

### `animation_inspect` mega tool

Actions:
- `actions`: list actions on object/armature.
- `fcurves`: return fcurve data (path, index, keyframes).
- `nla`: list NLA tracks/strips.
- `drivers`: list driver expressions, variables, targets.

### `animation_build` tool

Actions:
- `create_action`: create action and assign to object.
- `set_fcurves`: bulk create/update fcurves and keyframes.
- `set_drivers`: create drivers with variables/targets.
- `set_nla`: create NLA tracks/strips.

### Rules

- Use stable data paths from Blender RNA.
- Driver variables must include target object/bone/subtarget names.
- Chunking required for large keyframe sets.
- Blender 5.0+ compatible.

---

## 🧩 Implementation Checklist

| Layer | File | What to Add |
|------|------|-------------|
| Domain | `server/domain/tools/scene.py` or new `animation.py` | Animation interfaces |
| Application | `server/application/tool_handlers/*` | RPC wrappers |
| Adapter | `server/adapters/mcp/areas/animation.py` | `animation_inspect` / `animation_build` |
| Addon | `blender_addon/application/handlers/animation.py` | Blender animation handlers |
| Addon Init | `blender_addon/__init__.py` | Register RPC routes |
| Dispatcher | `server/adapters/mcp/dispatcher.py` | Tool map entries |
| Router Metadata | `server/router/infrastructure/tools_metadata/animation/*.json` | Tool metadata |
| Tests | `tests/unit/tools/animation/test_animation_tools.py` | Unit tests |

---

## ✅ Success Criteria

- Animation data can be exported and applied with round-trip fidelity.
- Drivers and NLA data are reconstructed reliably.
