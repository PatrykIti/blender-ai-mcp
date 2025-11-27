# TASK-014-3: Scene Inspect Object Tool

**Status:** ⏳ To Do  
**Priority:** 🔴 High  
**Phase:** Phase 7 - Introspection & Listing APIs

## 🎯 Objective
Deliver a deep inspection tool that returns structured data about a single object: type, transform, polycount, materials, modifiers, and custom metadata. This replaces unreliable visual inspection and is foundational for every later introspection tool.

## 🏗️ Architecture Requirements
### 1. Domain Layer (`server/domain/tools/scene_inspect_object.py`)
- Create Pydantic response model capturing object basics (type, collection names, active modifiers summary, material slot list, mesh stats).
- Define `ISceneInspectObjectTool.inspect(object_name: str) -> SceneObjectReport` with explicit error contracts (`ObjectNotFoundError`).

### 2. Application Layer (`server/application/handlers/scene_inspect_object_handler.py`)
- Handler validates input, calls RPC `scene.inspect_object`, and maps dictionaries into domain models.
- Provide helper to format the report string for MCP adapter (bullet list per section).

### 3. Adapter Layer
- Add `scene_inspect_object(ctx: Context, name: str) -> str` tool with docstring describing output sections and warnings (read-only, safe).
- Ensure errors (object missing) produce actionable guidance ("Use scene_list_objects first").

### 4. Blender Addon API (`blender_addon/api/scene_inspect_object_api.py`)
- Gather info without mode switching; use `obj.evaluated_get(depsgraph)` for accurate counts when modifiers applied.
- Return dict including: `object_name`, `type`, `dimensions`, `location`, `rotation`, `scale`, `collections`, `material_slots`, `modifier_stack`, `mesh_stats` (verts/edges/faces/triangles), `custom_properties` (safe subset).

### 5. RPC Server
- Register `scene.inspect_object` endpoint.

## ✅ Deliverables
- Domain interface, models, and accompanying exceptions (if not already defined).
- Application handler + DI binding.
- MCP adapter entry with clear formatting.
- Blender API + RPC registration.
- Documentation + changelog updates, README Phase 7 checklist.

## 🧪 Testing
- Inspect Mesh with modifiers/materials.
- Inspect non-mesh (Camera/Light) to ensure graceful handling of mesh stats.
- Invalid name -> user-friendly error.

## 📚 References
- `_docs/TOOLS_ARCHITECTURE_DEEP_DIVE.md`
- `README.md` Phase 7 scope description.
