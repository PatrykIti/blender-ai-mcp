# TASK-014-10: Scene Inspect Material Slots Tool

**Status:** ✅ Done
**Priority:** 🟡 Medium
**Phase:** Phase 7 - Introspection & Listing APIs
**Completion Date:** 2025-11-27

## 🎯 Objective
Design a scene-wide audit tool summarizing how materials are distributed across objects (slot usage, missing assignments, mismatched naming). This complements per-object queries by giving AI a holistic view for clean-up workflows.

## 🏗️ Architecture Requirements
### 1. Domain Layer (`server/domain/tools/scene_inspect_material_slots.py`)
- Request model options: `material_filter: Optional[str]`, `include_empty_slots: bool = True`.
- Response: list of `ObjectMaterialUsage` models (object name, slot_index, slot_name, material name, assigned_face_percentage, warnings array).
- Interface `ISceneInspectMaterialSlotsTool.inspect(request) -> SceneMaterialUsageReport`.

### 2. Application Layer (`server/application/handlers/scene_inspect_material_slots_handler.py`)
- Handler coordinates pagination if payload large (maybe chunk >200 slots) and ensures user-friendly string summarizing top issues.

### 3. Adapter Layer
- MCP tool signature: `scene_inspect_material_slots(material_filter: str | None = None, include_empty_slots: bool = True) -> str`.
- Docstring: `[SCENE][SAFE][READ-ONLY] Audits material slot assignments across scene.` Mention potential heavy runtime on large scenes.

### 4. Blender Addon API (`blender_addon/api/scene_inspect_material_slots_api.py`)
- Iterate all mesh objects, gather slot data, optionally compute face assignment ratios (requires temporary mode switch & bmesh read; follow context rules from TOOLS_ARCHITECTURE_DEEP_DIVE).
- Add warnings for slots referencing missing materials or duplicates.

### 5. RPC Server & Addon Registration
- Register `scene.inspect_material_slots` endpoint.
- **IMPORTANT:** Register handler in `blender_addon/__init__.py`:
  ```python
  rpc_server.register_handler("scene.inspect_material_slots", scene_handler.inspect_material_slots)
  ```

## ✅ Deliverables
- Domain contracts & models.
- Handler + DI binding.
- Adapter entry + docstring.
- Blender API implementation + RPC registration.
- Documentation updates + changelog + README Phase 7 check.

## 🧪 Testing
- Scenes with unused slots, missing materials, filters by material name.
- Performance test on object with many slots to ensure no blocking operations.

## 📚 References
- `_docs/TOOLS_ARCHITECTURE_DEEP_DIVE.md` for bmesh/mode switching patterns.
