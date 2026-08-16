---
type: task
id: TASK-008
title: Implement Modeling Tool - Apply Modifier
status: done
priority: medium
assignee: unassigned
depends_on: TASK-004
---

# 🎯 Objective
Implement a tool to apply (finalize) modifiers on an object, converting their effects into actual mesh geometry. This completes the core set of non-destructive modeling operations.

# 📋 Scope of Work

## 1. Domain Layer (`server/domain/tools/modeling.py`)
- Update `IModelingTool` interface with a new method:
  - `apply_modifier(name: str, modifier_name: str) -> str`

## 2. Blender Addon Logic (`blender_addon/application/handlers/modeling.py`)
- Implement `apply_modifier`:
  - Find the object by `name`.
  - Find the modifier by `modifier_name`.
  - Call `bpy.ops.object.modifier_apply(modifier=modifier_name)`.
  - Handle cases where the object or modifier is not found.

## 3. Application Layer (`server/application/tool_handlers/modeling_handler.py`)
- Implement the new method in `ModelingToolHandler` delegating to RPC.

## 4. Adapters Layer (`server/adapters/mcp/server.py`)
- Register the new tool:
  - `apply_modifier`

## 5. Testing (`tests/test_modeling_tools.py`)
- Add a unit test for `apply_modifier`:
  - Mock `bpy.ops.object.modifier_apply`.
  - Verify that the correct object and modifier name are passed.

# ✅ Acceptance Criteria
- AI can apply a specific modifier to a named object.
- The tool handles cases where the object or modifier does not exist gracefully (returns an error).
- Unit tests for the new tool pass successfully.
