---
type: task
id: TASK-004_Modeling_Tools
title: Modeling Tools (Mesh Ops) - Clean Architecture
status: done
priority: medium
assignee: unassigned
depends_on: TASK-003_4_Refactor_Addon_Architecture
---

# 🎯 Objective
Implement key geometry editing tools (primitives, modifiers) allowing AI to create simple 3D models.
Task must be executed according to **Clean Architecture** principles.

# 📋 Scope of Work (Domain & Application)

## 1. Domain Layer (`server/domain/`)
- **Create `server/domain/tools/modeling.py`**:
  - Interface `IModelingTool(ABC)`.
  - Methods: `create_primitive`, `transform_object`, `add_modifier`.

## 2. Application Layer (`server/application/`)
- **Create `server/application/tool_handlers/modeling_handler.py`**:
  - Class `ModelingToolHandler(IModelingTool)`.
  - Inject `IRpcClient`.

# 📋 Scope of Work (Infrastructure & Adapters)

## 3. Infrastructure (`server/infrastructure/di.py`)
- Update `di.py`: Add `get_modeling_handler()`.

## 4. Adapters (`server/adapters/mcp/server.py`)
- Add new MCP tools: `create_primitive`, `transform_object`, `add_modifier`.

# 📋 Scope of Work (Blender Addon)

## 5. Addon Application (`blender_addon/application/handlers/modeling.py`)
- Class `ModelingHandler`.
- Methods using `bpy.ops`.

## 6. Addon Infrastructure (`blender_addon/__init__.py`)
- Register `ModelingHandler` in `rpc_server`.

# ✅ Acceptance Criteria
- AI can create: Cube, Sphere, Cylinder, Plane.
- AI can move/rotate/scale objects.
- AI can add modifiers (e.g., Bevel).
- All operations follow Clean Architecture.