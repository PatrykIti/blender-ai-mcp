# TASK-014-1: Scene Get Mode Tool

**Status:** ✅ Complete  
**Priority:** 🟢 Low  
**Phase:** Phase 7 - Introspection & Listing APIs  
**Completion Date:** 2025-11-27

## 🎯 Objective
Expose a read-only MCP tool that reports Blender's current interaction mode (e.g., OBJECT, EDIT, SCULPT) so LLMs can branch logic without blindly attempting mode switches. The tool must strictly follow Clean Architecture boundaries and reuse existing DI patterns.

## 🏗️ Architecture Requirements
### 1. Domain Layer (`server/domain/tools/scene_get_mode.py`)
- Define a `SceneModeResponse` Pydantic model with `mode: Literal[...]` plus optional `details` (e.g., active object name).
- Define `ISceneGetModeTool` with `get_mode() -> SceneModeResponse` and document possible errors (e.g., Blender unavailable).

### 2. Application Layer (`server/application/handlers/scene_get_mode_handler.py`)
- Implement `SceneGetModeHandler(ISceneGetModeTool)` delegating to `RpcClient` (`scene.get_mode`).
- Ensure handler only depends on Domain contracts and serializes responses to friendly strings for adapters.

### 3. Adapter Layer (`server/adapters/mcp/server.py`)
- Register `scene_get_mode` MCP tool with docstring `[SCENE][SAFE][READ-ONLY] Reports current Blender mode.`
- Convert handler response into descriptive text ("Current mode: EDIT (active object: Cube)").

### 4. Blender Addon API (`blender_addon/api/scene_get_mode_api.py`)
- Implement `get_mode()` using `bpy.context.mode` and `bpy.context.active_object`.
- Return dictionaries with `status`, `mode`, `active_object`, `selected_object_names` (if cheap to compute) to keep adapters simple.

### 5. RPC Server (`blender_addon/rpc_server.py`)
- Register endpoint `scene.get_mode` pointing to the API function.
- Keep RPC layer thin; no business logic.

## ✅ Deliverables
- Domain interface + models.
- Application handler + DI binding.
- MCP adapter entry with exhaustive docstring.
- Blender addon API + RPC registration.
- Documentation updates: `_docs/_MCP_SERVER/scene_tools.md`, `_docs/_ADDON/scene_tools.md`, `_docs/_CHANGELOG/` entry, README Phase 7 checklist.

## 🧪 Testing
- Manual: switch between OBJECT/EDIT/SCULPT and verify returned mode.
- Error path: stop Blender RPC server and ensure handler surfaces readable error string.

## 📚 References
- `_docs/TOOLS_ARCHITECTURE_DEEP_DIVE.md` layering rules.
- `GEMINI.md` Clean Architecture summary.

## ✅ Completion Notes
- Added domain models/interface plus application handler + DI provider for `scene_get_mode`.
- Implemented Blender addon API, registered RPC command, and exposed MCP tool with structured response formatting.
- Extended unit test coverage (`tests/test_scene_mode.py`, new `tests/test_scene_get_mode_handler.py`).
- Updated README roadmap, `_docs/_ADDON`, `_docs/_MCP_SERVER`, architecture docs, and changelog per documentation policy.
- Verified via `poetry run pytest`.
