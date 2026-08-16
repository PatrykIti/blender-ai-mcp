# TASK-014-14: Scene Inspect Modifiers Tool

**Status:** ✅ Done
**Priority:** 🟡 Medium
**Phase:** Phase 7 - Introspection & Listing APIs
**Completion Date:** 2025-11-27

## 🎯 Objective
Implement a tool that audits modifier stacks for either a specific object or the entire scene, detailing order, configuration highlights, enabled states, and dependency warnings. AI agents need this to reason about destructive vs. non-destructive workflows.

## 🏗️ Architecture Requirements
### 1. Domain Layer (`server/domain/tools/scene_inspect_modifiers.py`)
- Request model: `object_name: Optional[str] = None`, `include_disabled: bool = True`.
- Response model: `ModifierSummary` (object_name, modifier_name, type, enabled_viewport/render, key properties dict, warnings list).
- Interface `ISceneInspectModifiersTool.inspect(request) -> SceneModifierReport`.

### 2. Application Layer (`server/application/handlers/scene_inspect_modifiers_handler.py`)
- Handler delegates to RPC `scene.inspect_modifiers`, converting dicts into domain models.
- When `object_name` omitted, aggregate results grouped by object and format accordingly.

### 3. Adapter Layer
- MCP tool `scene_inspect_modifiers(object_name: str | None = None, include_disabled: bool = True) -> str` with docstring `[SCENE][SAFE][READ-ONLY] Lists modifier stacks with key settings.`
- Warn about potential large outputs when scanning whole scene.

### 4. Blender Addon API (`blender_addon/api/scene_inspect_modifiers_api.py`)
- If `object_name` provided, inspect only that object; else iterate all mesh objects.
- Extract key properties depending on modifier type (e.g., Subdivision: levels/subdivision_type; Mirror: axes, merge threshold) but keep consistent schema.

### 5. RPC Registration & Addon Registration
- Register `scene.inspect_modifiers` endpoint.
- **IMPORTANT:** Register handler in `blender_addon/__init__.py`:
  ```python
  rpc_server.register_handler("scene.inspect_modifiers", scene_handler.inspect_modifiers)
  ```

## ✅ Deliverables
- Domain contracts & models.
- Handler + DI wiring.
- Adapter entry with docstring + validation.
- Blender API logic + RPC hook.
- Documentation updates + changelog + README.

## 🧪 Testing
- Object with multiple modifiers (Subdivision, Mirror) -> ensure details captured.
- Disabled modifiers included/excluded based on flag.
- Non-existent object -> descriptive error.

## 📚 References
- `_docs/TOOLS_ARCHITECTURE_DEEP_DIVE.md` for adapter/app/domain layering.
