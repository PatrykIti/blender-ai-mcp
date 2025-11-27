# TASK-014-9: Material List By Object Tool

**Status:** ⏳ To Do  
**Priority:** 🟢 Low  
**Phase:** Phase 7 - Introspection & Listing APIs

## 🎯 Objective
Provide per-object material slot insight, including slot names, linked materials, and assignment counts per face selection, allowing AI to validate if materials were assigned correctly.

## 🏗️ Architecture Requirements
### 1. Domain Layer (`server/domain/tools/material_list_by_object.py`)
- Request model: `object_name: str`, `include_indices: bool = False`.
- Response model: `MaterialSlotSummary` (slot_index, slot_name, material_name, uses_nodes, assigned_face_count optional, image_textures list).
- Interface `IMaterialListByObjectTool.list_materials(request) -> MaterialSlotsReport`.

### 2. Application Layer (`server/application/handlers/material_list_by_object_handler.py`)
- Handler resolves RPC `material.list_by_object`, handles errors for missing objects/non-mesh types.

### 3. Adapter Layer
- MCP tool `material_list_by_object(name: str, include_indices: bool = False) -> str` with docstring `[MATERIAL][SAFE][READ-ONLY] Lists material slots for given object.`

### 4. Blender Addon API (`blender_addon/api/material_list_by_object_api.py`)
- Validate object exists; ensure we can inspect `obj.material_slots` even for non-mesh? (if not, return helpful message).
- Optionally compute assigned face counts using `bmesh` when `include_indices=True` (warning: requires Edit Mode toggle; follow best practices from TOOLS_ARCHITECTURE_DEEP_DIVE to temporarily switch mode and restore state).

### 5. RPC Registration
- Add `material.list_by_object` endpoint.

## ✅ Deliverables
- Domain contracts.
- Handler + DI binding.
- Adapter tool + docstring.
- Blender API implementation + RPC registration.
- Docs + changelog + README update.

## 🧪 Testing
- Mesh with multiple material slots assigned to different faces.
- Object without materials -> message "Object has 0 material slots".

## 📚 References
- `_docs/TOOLS_ARCHITECTURE_DEEP_DIVE.md` (mode management section).
