---
type: task
id: TASK-007
title: Scene Tools Extension (Duplicate, Set Active, Viewport)
status: done
priority: high
assignee: unassigned
depends_on: TASK-003
---

# 🎯 Objective
Expand the capabilities of the Scene Tools to allow AI to duplicate objects, set the active object, and most importantly, "see" the scene using a viewport render.

# 📋 Scope of Work

## 1. Domain Layer (`server/domain/tools/scene.py`)
- Update `ISceneTool` interface with new methods:
  - `duplicate_object(name: str, translation: Optional[List[float]] = None) -> Dict[str, Any]`
  - `set_active_object(name: str) -> str`
  - `get_viewport(width: int = 1024, height: int = 768) -> str` (Returns Base64 encoded image)

## 2. Blender Addon Logic (`blender_addon/application/handlers/scene.py`)
- Implement `duplicate_object`:
  - Select object -> `bpy.ops.object.duplicate()` -> Translate.
- Implement `set_active_object`:
  - `bpy.context.view_layer.objects.active = obj`.
- Implement `get_viewport`:
  - Render scene using OpenGL (`bpy.ops.render.opengl`).
  - Use active camera or create a temporary one (Frame All).
  - Save to temp file -> Read bytes -> Encode Base64 -> Delete temp file.
  - Optimize for speed (Solid/LookDev mode, not full Cycles/Eevee render).

## 3. Application Layer (`server/application/tool_handlers/scene_handler.py`)
- Implement new methods in `SceneToolHandler` delegating to RPC.

## 4. Adapters Layer (`server/adapters/mcp/server.py`)
- Register new tools:
  - `duplicate_object`
  - `set_active_object`
  - `get_viewport` (Return type needs to be handled correctly for the AI to "see" it, likely Base64 string or MCP Image resource).

# ✅ Acceptance Criteria
- AI can duplicate an object and move it.
- AI can switch the active object (crucial for modifiers/editing).
- AI can request `get_viewport` and receive a visual representation of the scene (Base64 image).
