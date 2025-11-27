# TASK-014-4: Scene Snapshot State Tool

**Status:** ⏳ To Do  
**Priority:** 🟡 Medium  
**Phase:** Phase 7 - Introspection & Listing APIs

## 🎯 Objective
Add a tool that captures a lightweight JSON snapshot of the scene (object transforms, hierarchy, modifiers, selection) which the MCP server can store client-side for later diffing.

## 🏗️ Architecture Requirements
### 1. Domain Layer (`server/domain/tools/scene_snapshot_state.py`)
- Define `SceneSnapshotRequest` (fields like `include_mesh_stats: bool = False`, `include_materials: bool = False`).
- Define `SceneSnapshotResponse` with timestamp, hash (useful for change detection), and payload summary.
- Interface `ISceneSnapshotTool.create_snapshot(request) -> SceneSnapshotResponse`.

### 2. Application Layer (`server/application/handlers/scene_snapshot_state_handler.py`)
- Handler constructs request model, calls RPC `scene.snapshot_state`, and returns serialized string (store base64/JSON?).
- Provide helper to persist snapshot to temp dir if requested via env (mirror existing viewport temp logic) – keep optional.

### 3. Adapter Layer
- Add MCP tool `scene_snapshot_state(include_mesh_stats: bool = False, include_materials: bool = False) -> str`.
- Docstring: `[SCENE][READ-ONLY] Captures serialized snapshot for later comparisons; large payloads possible when toggles are true.`

### 4. Blender Addon API (`blender_addon/api/scene_snapshot_state_api.py`)
- Iterate all objects, capturing core metadata and optional extras.
- Generate deterministic ordering, compute hash (e.g., SHA256 of JSON string) to detect changes.

### 5. RPC Server
- Register `scene.snapshot_state` endpoint.

## ✅ Deliverables
- Domain models & interface.
- Application handler + DI binding.
- Adapter registration with safe parameter validation.
- Blender API + RPC hook.
- Docs: `_docs/_MCP_SERVER/scene_tools.md`, `_docs/_ADDON/scene_tools.md`, `_docs/_CHANGELOG/` entry, README checklist.

## 🧪 Testing
- Snapshot in simple scene; verify JSON stored and hash stable unless modifications.
- Toggle optional flags and ensure payload size/fields change accordingly.

## 📚 References
- `_docs/TOOLS_ARCHITECTURE_DEEP_DIVE.md`
- Task 013 (Viewport Output Modes) for temp-dir inspiration.
