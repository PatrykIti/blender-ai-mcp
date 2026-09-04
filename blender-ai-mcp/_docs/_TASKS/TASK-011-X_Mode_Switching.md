# TASK-011-X: Scene Mode Switching

## 🎯 Objective
Implement a dedicated tool to explicitly change the Blender interaction mode (`OBJECT`, `EDIT`, `SCULPT`, etc.). This gives the AI better control over the state and allows recovery from incorrect modes.

## 📋 Requirements

### 1. Interface
*   Add `set_mode(mode: str) -> str` to `ISceneTool`.

### 2. Implementation
*   Use `bpy.ops.object.mode_set(mode=mode)`.
*   Validate that an active object exists for modes other than OBJECT.

## ✅ Checklist
- [x] Update Interface & Handlers.
- [x] Register `scene_set_mode`.
- [x] Add Tests (`tests/test_scene_mode.py`).
