# 39 - Organic & Vertex Group Tools (TASK-016 & TASK-017)

**Date:** 2025-11-29
**Version:** 1.13.0

## Summary

Implemented Phase 2.2 (Organic & Deform) and Phase 2.3 (Vertex Groups) mesh tools for organic surface manipulation and vertex group management.

## New Tools

### Phase 2.2: Organic & Deform

| Tool | Description | Tag |
|------|-------------|-----|
| `mesh_randomize` | Randomizes vertex positions for organic surface variations | `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE]` |
| `mesh_shrink_fatten` | Moves vertices along their normals (inflate/deflate) | `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE]` |

### Phase 2.3: Vertex Groups

| Tool | Description | Tag |
|------|-------------|-----|
| `mesh_create_vertex_group` | Creates a new vertex group on mesh object | `[MESH][SAFE]` |
| `mesh_assign_to_group` | Assigns selected vertices to vertex group with weight | `[EDIT MODE][SELECTION-BASED][SAFE]` |
| `mesh_remove_from_group` | Removes selected vertices from vertex group | `[EDIT MODE][SELECTION-BASED][SAFE]` |

## Files Changed

### Server (MCP)
- `server/domain/tools/mesh.py` - Added interface methods
- `server/application/tool_handlers/mesh_handler.py` - Added RPC bridge implementations
- `server/adapters/mcp/areas/mesh.py` - Added MCP tool definitions with docstrings

### Blender Addon
- `blender_addon/application/handlers/mesh.py` - Added Blender implementations
- `blender_addon/__init__.py` - Registered new RPC handlers

### Tests
- `tests/test_mesh_organic_groups.py` - Added 16 pytest-style tests

## API Details

### mesh_randomize
```python
mesh_randomize(
    amount: float = 0.1,      # Maximum displacement
    uniform: float = 0.0,     # Uniform random factor (0-1)
    normal: float = 0.0,      # Normal-based factor (0-1)
    seed: int = 0             # Random seed (0 = random)
)
```

### mesh_shrink_fatten
```python
mesh_shrink_fatten(
    value: float              # Distance along normals (+outward, -inward)
)
```

### mesh_create_vertex_group
```python
mesh_create_vertex_group(
    object_name: str,         # Target mesh object
    name: str                 # Name for new group
)
```

### mesh_assign_to_group
```python
mesh_assign_to_group(
    object_name: str,         # Target mesh object
    group_name: str,          # Vertex group name
    weight: float = 1.0       # Weight value (0.0-1.0)
)
```

### mesh_remove_from_group
```python
mesh_remove_from_group(
    object_name: str,         # Target mesh object
    group_name: str           # Vertex group name
)
```

## Tests

All 16 new tests passing:
- `TestMeshRandomize` (3 tests)
- `TestMeshShrinkFatten` (3 tests)
- `TestMeshCreateVertexGroup` (4 tests)
- `TestMeshAssignToGroup` (3 tests)
- `TestMeshRemoveFromGroup` (3 tests)

Total project tests: 179 passed, 19 skipped.

## Related Tasks
- TASK-016-1: Mesh Randomize Tool ✅
- TASK-016-2: Mesh Shrink/Fatten Tool ✅
- TASK-017-1: Mesh Create Vertex Group Tool ✅
- TASK-017-2: Mesh Assign/Remove Vertex Group Tools ✅
