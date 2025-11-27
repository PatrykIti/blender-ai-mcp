# TASK-014-8: Material List Tool

**Status:** ⏳ To Do  
**Priority:** 🟢 Low  
**Phase:** Phase 7 - Introspection & Listing APIs

## 🎯 Objective
List all materials in the blend file with essential parameters (BSDF type, color, roughness, metallic, node usage) so AI agents can reason about look-dev without opening the shader editor.

## 🏗️ Architecture Requirements
### 1. Domain Layer (`server/domain/tools/material_list.py`)
- Define `MaterialSummary` model capturing `name`, `use_nodes`, `base_color`, `roughness`, `metallic`, `alpha`, `assigned_object_count`.
- Interface `IMaterialListTool.list_materials(include_unassigned: bool = True) -> List[MaterialSummary]`.

### 2. Application Layer (`server/application/handlers/material_list_handler.py`)
- Handler calls RPC `material.list`, optionally filters results, and formats output table.

### 3. Adapter Layer
- MCP tool signature: `material_list(include_unassigned: bool = True) -> str`.
- Docstring: `[MATERIAL][SAFE][READ-ONLY] Lists materials with key shader parameters and assignment counts.`

### 4. Blender Addon API (`blender_addon/api/material_list_api.py`)
- Iterate `bpy.data.materials`, inspect `material.use_nodes` and Principled BSDF default socket values when available.
- Count object assignments by scanning `obj.material_slots` (efficient approach recommended, e.g., dictionary building once).

### 5. RPC Server
- Register `material.list` endpoint.

## ✅ Deliverables
- Domain contract + models.
- Application handler w/ DI.
- Adapter entry with thorough docstring.
- Blender API + RPC registration.
- Docs + changelog + README update.

## 🧪 Testing
- Scenes with different material types (node-based vs. simple).
- Materials unused by objects when `include_unassigned=False`.

## 📚 References
- `_docs/TOOLS_ARCHITECTURE_DEEP_DIVE.md`.
