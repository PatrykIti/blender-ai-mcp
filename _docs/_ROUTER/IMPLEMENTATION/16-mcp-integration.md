# 16. MCP Integration Adapter

**Task:** TASK-039-17
**Status:** Done
**Layer:** Adapters

---

## Overview

The MCP Integration Adapter hooks the Router Supervisor into the MCP server tool execution pipeline. It wraps tool executors to route all calls through the supervisor.

---

## Implementation

**File:** `server/router/adapters/mcp_integration.py`

### MCPRouterIntegration

Main integration class that wraps tool executors:

```python
from server.router.adapters import MCPRouterIntegration

# Create integration
integration = MCPRouterIntegration(enabled=True)
integration.set_rpc_client(rpc_client)

# Wrap executor
async def original_executor(tool_name: str, params: dict) -> str:
    return await execute_tool(tool_name, params)

wrapped = integration.wrap_tool_executor(original_executor)

# Now all calls go through router
result = await wrapped("mesh_extrude_region", {"depth": 0.5})
```

### RouterMiddleware

Middleware-style integration:

```python
from server.router.adapters import RouterMiddleware

middleware = RouterMiddleware()
wrapped_handler = middleware(original_handler)
```

### Factory Function

```python
from server.router.adapters import create_router_integration

integration = create_router_integration(
    config=RouterConfig(),
    rpc_client=rpc_client,
    enabled=True,
    bypass_tools=["system_info", "scene_list"],  # Skip routing
)
```

---

## Features

1. **Async & Sync Support**
   - `wrap_tool_executor()` for async executors
   - `wrap_sync_executor()` for sync executors

2. **Bypass Tools**
   - Skip routing for specific tools
   - Useful for read-only operations

3. **Enable/Disable**
   - Runtime toggle for routing
   - Graceful fallback on errors

4. **Result Combining**
   - Multi-step results combined intelligently
   - Step numbers and tool names included

5. **Statistics**
   - Execution counts
   - Error tracking
   - Router stats integration

---

## Usage

### Basic Usage

```python
integration = MCPRouterIntegration()

# Wrap your tool executor
wrapped = integration.wrap_tool_executor(my_executor)

# Use wrapped executor
result = await wrapped("mesh_bevel", {"width": 0.1})
```

### With Bypass

```python
integration = MCPRouterIntegration()
integration.add_bypass_tool("scene_list")  # Skip routing

# This goes through router:
await wrapped("mesh_extrude_region", {})

# This bypasses router:
await wrapped("scene_list", {})
```

### Get Stats

```python
stats = integration.get_stats()
# {
#     "enabled": True,
#     "execution_count": 100,
#     "error_count": 2,
#     "bypass_tools": ["scene_list"],
#     "router_stats": {...}
# }
```

---

## Tests

**File:** `tests/unit/router/adapters/test_mcp_integration.py`

32 unit tests covering:
- Initialization
- Enable/disable
- Bypass functionality
- Async executor wrapping
- Sync executor wrapping
- Result combining
- Statistics
- Factory function
- Full pipeline integration

---

## See Also

- [15-supervisor-router.md](./15-supervisor-router.md) - SupervisorRouter
- [17-logging-telemetry.md](./17-logging-telemetry.md) - Logging
