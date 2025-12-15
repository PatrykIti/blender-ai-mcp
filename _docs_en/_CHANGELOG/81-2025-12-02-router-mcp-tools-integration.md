# 81 - Router MCP Tools Integration

**Date:** 2025-12-02
**Status:** Done
**Task:** TASK-039 (Router Supervisor Implementation)

## Summary

Wrapped all 119 MCP tools with `route_tool_call()` to integrate the Router Supervisor into the tool execution pipeline.

## Changes

### Files Modified

| File | Tools Wrapped |
|------|---------------|
| `server/adapters/mcp/areas/baking.py` | 4 tools |
| `server/adapters/mcp/areas/collection.py` | 3 tools |
| `server/adapters/mcp/areas/curve.py` | 2 tools |
| `server/adapters/mcp/areas/lattice.py` | 3 tools |
| `server/adapters/mcp/areas/material.py` | 6 tools |
| `server/adapters/mcp/areas/mesh.py` | ~45 tools |
| `server/adapters/mcp/areas/modeling.py` | 14 tools |
| `server/adapters/mcp/areas/scene.py` | 12 tools |
| `server/adapters/mcp/areas/sculpt.py` | 13 tools |
| `server/adapters/mcp/areas/system.py` | 13 tools |
| `server/adapters/mcp/areas/uv.py` | 4 tools |

**Total: ~119 tools**

### Wrapping Pattern

Each tool now uses the `route_tool_call()` wrapper:

```python
@mcp.tool()
def mesh_extrude_region(ctx: Context, move: Optional[List[float]] = None) -> str:
    """[EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Extrudes selected region..."""
    return route_tool_call(
        tool_name="mesh_extrude_region",
        params={"move": move},
        direct_executor=lambda: get_mesh_handler().extrude_region(move)
    )
```

Two patterns used:
1. **Simple lambda** - for tools with straightforward handler calls
2. **Nested execute() function** - for tools with complex logic (parsing, ctx.info(), formatting)

### Behavior

- **ROUTER_ENABLED=false** (default): Tools pass through directly via `direct_executor`
- **ROUTER_ENABLED=true**: Router intercepts, logs with `[ROUTER]` prefix at INFO level, performs analysis/correction

## Technical Details

- Import added to each area file: `from server.adapters.mcp.router_helper import route_tool_call`
- Internal helper functions (prefixed with `_`) not wrapped - called by mega-tools
- All imports verified working via `poetry run python` test

## Testing

- All area modules import successfully
- Docker image rebuilt: `blender-mcp-server:latest`

## Usage

```bash
# Without router (default)
docker run -i --rm blender-mcp-server

# With router enabled
docker run -i --rm -e ROUTER_ENABLED=true blender-mcp-server
```
