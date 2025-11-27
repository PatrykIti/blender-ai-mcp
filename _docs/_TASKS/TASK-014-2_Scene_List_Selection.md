# TASK-014-2: Scene List Selection Tool

**Status:** ⏳ To Do  
**Priority:** 🟡 Medium  
**Phase:** Phase 7 - Introspection & Listing APIs

## 🎯 Objective
Provide a deterministic tool that reports current selection state (objects in Object Mode, components in Edit Mode) so AI agents can verify assumptions before destructive actions.

## 🏗️ Architecture Requirements
### 1. Domain Layer (`server/domain/tools/scene_list_selection.py`)
- Define request/response Pydantic models capturing mode, selected object names, and when in Edit Mode, counts of selected verts/edges/faces.
- Interface `ISceneListSelectionTool.list_selection() -> SceneSelectionSummary`.

### 2. Application Layer (`server/application/handlers/scene_list_selection_handler.py`)
- Handler calls RPC `scene.list_selection` and converts dicts into response models.
- Provide readable summaries for adapter (e.g., "3 objects selected: Cube, Light, Camera").

### 3. Adapter Layer (`server/adapters/mcp/server.py`)
- Add MCP tool `scene_list_selection(ctx: Context) -> str` with docstring `[SCENE][SAFE][READ-ONLY] Lists current selection in Object/Edit mode.`
- Ensure response highlights both counts and names.

### 4. Blender Addon API (`blender_addon/api/scene_list_selection_api.py`)
- Implement logic that inspects `bpy.context.selected_objects` plus `bmesh` queries when in Edit Mode (counts only to avoid heavy payloads).
- Include safeguards for missing `bpy.context.edit_object`.

### 5. RPC Server
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
