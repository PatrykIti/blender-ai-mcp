# TASK-014-2: Scene List Selection Tool

**Status:** ✅ Complete  
**Priority:** 🟡 Medium  
**Phase:** Phase 7 - Introspection & Listing APIs  
**Completion Date:** 2025-11-27

## 🎯 Objective
Provide a deterministic tool that reports current selection state (objects in Object Mode, components in Edit Mode) so AI agents can verify assumptions before destructive actions.

## 🏗️ Architecture Requirements
### 1. Domain Layer (`server/domain/tools/scene.py`)
- Extend `ISceneTool` with `list_selection()` returning a structured dict (mode, selected objects, optional Edit Mode counts).

### 2. Application Layer (`server/application/tool_handlers/scene_handler.py`)
- Implement `list_selection()` by forwarding RPC `scene.list_selection` and returning the dict to adapters.

### 3. Adapter Layer (`server/adapters/mcp/server.py`)
- Add MCP tool `scene_list_selection(ctx: Context) -> str` with docstring `[SCENE][SAFE][READ-ONLY] ...` and format summary text for AI clients.

### 4. Blender Addon API (`blender_addon/application/handlers/scene.py`)
- Implement logic that inspects `bpy.context.selected_objects` plus `bmesh` queries when in Edit Mode (counts only to avoid heavy payloads).
- Include safeguards for missing `bpy.context.edit_object`.

### 5. RPC Server (`blender_addon/__init__.py`)
- Register `scene.list_selection` endpoint.

## ✅ Deliverables
- Domain models/interface.
- Handler + DI wiring.
- MCP adapter registration.
- Blender API + RPC hook.
- Documentation updates + changelog + README checklist.

## 🧪 Testing
- Object Mode: select multiple objects, verify listing.
- Edit Mode: select vertices on mesh, confirm counts.
- Empty selection: ensure graceful "No selection" message.

## 📚 References
- `_docs/TOOLS_ARCHITECTURE_DEEP_DIVE.md`
- Existing `scene_list_objects` task for tone.

## ✅ Completion Notes
- Extended `ISceneTool`/`SceneToolHandler` with `get_mode`/`list_selection` returning structured dicts, keeping Clean Architecture intact.
- Implemented Blender addon logic (object + edit mode counts), registered RPC handler, and exposed new MCP tool with formatted summary.
- Updated documentation (README, `_docs` knowledge base, changelog) and added tests (`tests/test_scene_mode.py`, `tests/test_scene_get_mode_handler.py`).
- Verified via `PYTHONPATH=. poetry run pytest`.
