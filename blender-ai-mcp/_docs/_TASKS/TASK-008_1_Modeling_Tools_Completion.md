---
type: task
id: TASK-008_1
title: Modeling Tools Completion (Object Mode)
status: done
priority: high
assignee: unassigned
depends_on: TASK-008
---

# 🎯 Objective
Complete the implementation of **Modeling Tools** (Object Mode) based on the specifications in `_docs/MODELING_TOOLS_ARCHITECTURE.md`. This task focuses on object-level operations that manage geometry containers, origins, and types, ensuring full compliance with the architecture document.

# 📋 Scope of Work

## 1. Domain Layer (`server/domain/tools/modeling.py`)
- Update `IModelingTool` interface with new methods:
  - `convert_to_mesh(name: str) -> str`
  - `join_objects(object_names: List[str]) -> str`
  - `separate_object(name: str, type: str = "LOOSE") -> List[str]` (Types: "LOOSE", "SELECTED", "MATERIAL")
  - `set_origin(name: str, type: str = "GEOMETRY", center: str = "MEDIAN") -> str` (Types: "GEOMETRY", "ORIGIN_CURSOR", "ORIGIN_GEOMETRY")

## 2. Blender Addon Logic (`blender_addon/application/handlers/modeling.py`)
- Implement `convert_to_mesh`:
  - Converts Curves, Surfaces, or Text objects to Mesh.
  - Uses `bpy.ops.object.convert(target='MESH')`.
- Implement `join_objects`:
  - Validates all objects exist.
  - Selects them, makes the last one active.
  - Calls `bpy.ops.object.join()`.
- Implement `separate_object`:
  - Enters Edit Mode momentarily if needed or uses `bpy.ops.mesh.separate`.
  - Returns list of new object names.
- Implement `set_origin`:
  - Calls `bpy.ops.object.origin_set(type=..., center=...)`.

## 3. Application Layer (`server/application/tool_handlers/modeling_handler.py`)
- Implement new methods in `ModelingToolHandler` delegating to RPC.

## 4. Adapters Layer (`server/adapters/mcp/server.py`)
- Register new MCP tools:
  - `convert_to_mesh`
  - `join_objects`
  - `separate_object`
  - `set_origin`

## 5. Blender Addon Entry Point (`blender_addon/__init__.py`)
- Register new RPC handlers for all new tools.

## 6. Refactoring & Alignment
- Ensure existing tools align with `MODELING_TOOLS_ARCHITECTURE.md`.
  - `add_modifier` is already groupable (OK).
  - `apply_modifier` is separate (OK).
  - `create_primitive` handles basic primitives (OK).
- Ensure argument naming consistency across all modeling tools.

## 7. Testing (`tests/test_modeling_tools.py`)
- Add unit tests for all new tools.
- Verify correct `bpy.ops` calls and error handling (e.g. joining non-existent objects).

# ✅ Acceptance Criteria
- AI can convert curves/text to mesh.
- AI can join multiple objects into one.
- AI can separate a mesh into loose parts.
- AI can reset object origin to geometry center.
- All new tools follow the "Object Mode" constraint.
