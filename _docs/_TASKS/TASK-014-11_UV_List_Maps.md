# TASK-014-11: UV List Maps Tool

**Status:** ⏳ To Do  
**Priority:** 🟡 Medium  
**Phase:** Phase 7 - Introspection & Listing APIs

## 🎯 Objective
Create a tool that reports UV map information for a specified mesh object: map names, active flag, texture assignment counts, and optional island stats. This helps LLMs plan UV workflows deterministically.

## 🏗️ Architecture Requirements
### 1. Domain Layer (`server/domain/tools/uv_list_maps.py`)
- Request model: `object_name: str`, `include_island_counts: bool = False`.
- Response model `UVMapSummary` capturing `name`, `is_active_render`, `is_active`, `has_pinned_islands`, `face_count`.
- Interface `IUVListMapsTool.list_maps(request) -> UVMapReport`.

### 2. Application Layer (`server/application/handlers/uv_list_maps_handler.py`)
- Handler delegates to RPC `uv.list_maps`; ensure errors for non-mesh objects are friendly.

### 3. Adapter Layer
- MCP tool `uv_list_maps(object_name: str, include_island_counts: bool = False) -> str` with docstring `[UV][SAFE][READ-ONLY] Lists UV maps on mesh object.`

### 4. Blender Addon API (`blender_addon/api/uv_list_maps_api.py`)
- Access `obj.data.uv_layers`; compute counts (use `len(layer.data)` / 2 to derive face loops?).
- For optional island counts, rely on `bmesh.ops.find_doubles`? (Alternatively, skip heavy computation and document as not implemented yet.)
- Validate mode; stay in Object Mode when possible.

### 5. RPC Server & Addon Registration
- Register `uv.list_maps` endpoint.
- **IMPORTANT:** Register handler in `blender_addon/__init__.py`:
  ```python
  # UV
  uv_handler = UVHandler()
  rpc_server.register_handler("uv.list_maps", uv_handler.list_maps)
  ```

## ✅ Deliverables
- Domain contracts.
- Handler + DI binding.
- Adapter registration.
- Blender API implementation + RPC hook.
- Docs + changelog + README update.

## 🧪 Testing
- Mesh with multiple UV maps (active render vs. inactive).
- Object without UV maps -> "Object has 0 UV maps" message.

## 📚 References
- `_docs/TOOLS_ARCHITECTURE_DEEP_DIVE.md` (object vs. edit mode guidance).
