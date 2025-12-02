# Router Quick Start

Get started with Router Supervisor in 5 minutes.

---

## Prerequisites

- Python 3.10+
- Poetry
- Blender 4.0+ with addon installed
- ~2GB RAM for LaBSE model

---

## Installation

Router is included with the MCP server. No additional installation needed.

```bash
# Install dependencies (includes sentence-transformers)
poetry install

# Start MCP server
poetry run python server/main.py
```

---

## Basic Usage

### 1. Create Router Instance

```python
from server.router.application.router import SupervisorRouter
from server.router.infrastructure.config import RouterConfig

# Create with default settings
router = SupervisorRouter()

# Or with custom config
config = RouterConfig(
    auto_mode_switch=True,
    auto_selection=True,
    clamp_parameters=True,
)
router = SupervisorRouter(config=config, rpc_client=rpc_client)
```

### 2. Process LLM Tool Call

```python
# LLM wants to extrude (but scene is in OBJECT mode, no selection)
tools = router.process_llm_tool_call(
    tool_name="mesh_extrude_region",
    params={"depth": 0.5},
    prompt="extrude the top face"
)

# Router returns corrected sequence:
# [
#     {"tool": "system_set_mode", "params": {"mode": "EDIT"}},
#     {"tool": "mesh_select", "params": {"action": "all"}},
#     {"tool": "mesh_extrude_region", "params": {"depth": 0.5}}
# ]
```

### 3. Execute Tools

```python
for tool in tools:
    tool_name = tool["tool"]
    params = tool["params"]

    # Convert to RPC format
    area = tool_name.split("_")[0]
    method = "_".join(tool_name.split("_")[1:])

    result = rpc_client.send_request(f"{area}.{method}", params)
    print(f"{tool_name}: {result}")
```

---

## What Router Does

Router intercepts LLM tool calls and:

1. **Fixes Mode** - Adds `system_set_mode` if tool requires different mode
2. **Adds Selection** - Adds `mesh_select` if tool needs selection
3. **Clamps Parameters** - Prevents invalid values (e.g., bevel > object size)
4. **Expands Workflows** - Replaces single tool with workflow for detected patterns
5. **Blocks Invalid** - Prevents operations that would crash

---

## Example: Phone Screen Cutout

```python
# Create phone-like object
rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
rpc_client.send_request("modeling.transform_object", {"scale": [0.4, 0.8, 0.05]})

# LLM asks to extrude (for screen cutout)
tools = router.process_llm_tool_call(
    "mesh_extrude_region",
    {"depth": -0.02},
    prompt="create screen cutout"
)

# Router detects phone_like pattern and returns:
# 1. Switch to EDIT mode
# 2. Select all faces
# 3. Inset face (screen border)
# 4. Extrude inward (screen recess)
```

---

## Next Steps

- [CONFIGURATION.md](./CONFIGURATION.md) - All config options
- [PATTERNS.md](./PATTERNS.md) - Geometry pattern reference
- [API.md](./API.md) - Full API documentation
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Common issues

---

## Quick Reference

| Feature | Default | Description |
|---------|---------|-------------|
| Mode auto-switch | ✅ On | Fix OBJECT/EDIT/SCULPT mode |
| Auto-selection | ✅ On | Add selection if missing |
| Parameter clamping | ✅ On | Clamp to valid ranges |
| Pattern workflows | ✅ On | Expand to workflows |
| Intent classifier | ✅ On | LaBSE multilingual |
