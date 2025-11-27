# TASK-014-13: Scene Inspect Mesh Topology Tool

**Status:** ⏳ To Do  
**Priority:** 🔴 High  
**Phase:** Phase 7 - Introspection & Listing APIs

## 🎯 Objective
Add a diagnostics tool that reports detailed topology stats for a given mesh: vertex/edge/face counts, triangle/quads, non-manifold elements, loose geometry, normals consistency. This helps AI detect geometry issues before proceeding.

## 🏗️ Architecture Requirements
### 1. Domain Layer (`server/domain/tools/scene_inspect_mesh_topology.py`)
- Request model: `object_name: str`, `detailed: bool = False` (to toggle expensive checks like non-manifold detection).
- Response model: `MeshTopologyReport` capturing counts, booleans (has_ngons, has_loose_verts), optional arrays (problem_indices limited to e.g., 50 entries).
- Interface `ISceneInspectMeshTopologyTool.inspect(request) -> MeshTopologyReport`.

### 2. Application Layer (`server/application/handlers/scene_inspect_mesh_topology_handler.py`)
- Handler validates target is mesh, triggers RPC `scene.inspect_mesh_topology`, formats summary.

### 3. Adapter Layer
- MCP tool `scene_inspect_mesh_topology(object_name: str, detailed: bool = False) -> str` with docstring `[MESH][SAFE][READ-ONLY] Reports topology health metrics.`

### 4. Blender Addon API (`blender_addon/api/scene_inspect_mesh_topology_api.py`)
- Use `bmesh` in Edit Mode or `bmesh.new()` with `from_mesh` to analyze data without altering mode.
- Compute: vertex/edge/face counts, triangles/quads/ngons, `len(bm.verts)` etc., run `bmesh.ops.find_doubles`? (Better: use `bm.calc_face_angle`, `bm.calc_loop_triangles`).
- Identify non-manifold edges via `not e.is_manifold`.

### 5. RPC Registration
- Register `scene.inspect_mesh_topology` endpoint.

## ✅ Deliverables
- Domain contracts.
- Handler + DI binding.
- Adapter entry with thorough docstring + warnings about heavy mode.
- Blender API + RPC hook.
- Documentation + changelog + README update (mark Phase 7 item in checklist once done).

## 🧪 Testing
- Cube (clean) -> no issues.
- Mesh with intentional non-manifold edges/loose verts -> flagged.
- Non-mesh object -> descriptive error.

## 📚 References
- `_docs/TOOLS_ARCHITECTURE_DEEP_DIVE.md` (bmesh best practices).
