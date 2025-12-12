# Adding New Tools to Router

Guide for updating Router Supervisor when adding new MCP tools.

---

## Quick Checklist

When adding a new tool to the project, update these router components:

| Step | Required | File/Location | Description |
|------|----------|---------------|-------------|
| 1. Tool Metadata | **Yes** | `server/router/infrastructure/tools_metadata/{category}/` | JSON metadata file |
| 2. Firewall Rules | If needed | `server/router/application/engines/error_firewall.py` | Validation rules |
| 3. Override Rules | If needed | `server/router/application/engines/tool_override_engine.py` | Pattern-based overrides |
| 4. Workflows | If needed | `server/router/infrastructure/workflows/` | YAML/JSON workflow definitions |
| 5. Unit Tests | **Yes** | `tests/unit/router/` | Test new metadata/rules |

---

## Step 1: Create Tool Metadata (Required)

### Location
```
server/router/infrastructure/tools_metadata/{category}/{tool_name}.json
```

### Categories
- `mesh/` - Edit Mode mesh operations
- `modeling/` - Object Mode modeling
- `scene/` - Scene management
- `system/` - System operations (mode, export, import)
- `material/` - Material operations
- `uv/` - UV mapping
- `curve/` - Curve operations
- `collection/` - Collection management
- `lattice/` - Lattice deformation
- `sculpt/` - Sculpt tools
- `baking/` - Baking operations

### Schema Reference

```json
{
  "tool_name": "mesh_new_tool",
  "category": "mesh",
  "mode_required": "EDIT",
  "selection_required": true,
  "keywords": ["keyword1", "keyword2", "action verb"],
  "sample_prompts": [
    "do the thing with the mesh",
    "apply new tool to selection"
  ],
  "parameters": {
    "param_name": {
      "type": "float",
      "default": 0.1,
      "range": [0.0, 1.0],
      "description": "What this parameter does"
    }
  },
  "related_tools": ["mesh_extrude_region", "mesh_bevel"],
  "patterns": ["phone_like:specific_use"],
  "description": "Human-readable description of what the tool does."
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `tool_name` | string | Unique identifier matching MCP tool name |
| `category` | string | One of: scene, system, modeling, mesh, material, uv, curve, collection, lattice, sculpt, baking |
| `mode_required` | string | One of: OBJECT, EDIT, SCULPT, VERTEX_PAINT, WEIGHT_PAINT, TEXTURE_PAINT, ANY |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `selection_required` | boolean | false | Whether tool needs geometry selection |
| `keywords` | array | [] | Keywords for intent classification |
| `sample_prompts` | array | [] | Example prompts (for classifier training) |
| `parameters` | object | {} | Parameter definitions with types and ranges |
| `related_tools` | array | [] | Tools commonly used together |
| `patterns` | array | [] | Associated geometry patterns |
| `description` | string | "" | Human-readable description |

### Parameter Types

| Type | Range Format | Example |
|------|--------------|---------|
| `float` | `[min, max]` | `"range": [0.0, 10.0]` |
| `int` | `[min, max]` | `"range": [1, 100]` |
| `bool` | N/A | `"default": true` |
| `enum` | Use `options` | `"options": ["A", "B", "C"]` |
| `string` | N/A | `"default": "name"` |
| `vector3` | N/A | `"default": [0, 0, 0]` |
| `array` | N/A | `"default": []` |

### Example: Complete Tool Metadata

```json
{
  "tool_name": "mesh_bevel",
  "category": "mesh",
  "mode_required": "EDIT",
  "selection_required": true,
  "keywords": ["bevel", "round", "chamfer", "smooth edges", "soften"],
  "sample_prompts": [
    "bevel the edges",
    "round the corners",
    "chamfer the selected edges",
    "smooth the edges",
    "add bevel to all edges"
  ],
  "parameters": {
    "offset": {
      "type": "float",
      "default": 0.1,
      "range": [0.001, 10.0],
      "description": "Bevel size (offset)"
    },
    "segments": {
      "type": "int",
      "default": 1,
      "range": [1, 10],
      "description": "Number of bevel segments"
    },
    "affect": {
      "type": "enum",
      "options": ["EDGES", "VERTICES"],
      "default": "EDGES",
      "description": "What to bevel"
    }
  },
  "related_tools": ["mesh_extrude_region", "mesh_inset", "mesh_select"],
  "patterns": ["phone_like:edge_rounding", "box_like:chamfer"],
  "description": "Bevels selected edges or vertices to create rounded or chamfered edges."
}
```

---

## Step 2: Add Firewall Rules (If Needed)

Add rules if the tool:
- Requires specific mode
- Requires selection
- Has parameters that should be validated/clamped
- Can fail in certain states

### Location
```python
# server/router/application/engines/error_firewall.py
# In _register_default_rules() method
```

### Rule Types

#### Mode Violation Rule (auto-fix)
```python
self.register_rule(
    rule_name="new_tool_wrong_mode",
    tool_pattern="mesh_new_tool",
    condition="mode == 'OBJECT'",
    action="auto_fix",
    fix_description="Switch to EDIT mode",
)
```

#### Selection Required Rule (auto-fix)
```python
self.register_rule(
    rule_name="new_tool_no_selection",
    tool_pattern="mesh_new_tool",
    condition="no_selection",
    action="auto_fix",
    fix_description="Select all geometry",
)
```

#### Parameter Clamping Rule (modify)
```python
self.register_rule(
    rule_name="new_tool_param_too_large",
    tool_pattern="mesh_new_tool",
    condition="param:value > dimension_ratio:0.5",
    action="modify",
    fix_description="Clamp parameter value",
)
```

#### Blocking Rule (block)
```python
self.register_rule(
    rule_name="new_tool_invalid_state",
    tool_pattern="mesh_new_tool",
    condition="no_objects",
    action="block",
    fix_description="",
)
```

### Available Conditions

| Condition | Description |
|-----------|-------------|
| `mode == 'MODE'` | Current mode equals MODE |
| `mode != 'MODE'` | Current mode not equals MODE |
| `no_selection` | No geometry selected |
| `no_objects` | No objects in scene |
| `param:name > value` | Parameter exceeds value |
| `param:name < value` | Parameter below value |
| `dimension_ratio:factor` | Relative to object size |

### Available Actions

| Action | Behavior |
|--------|----------|
| `auto_fix` | Add pre-steps to fix issue |
| `modify` | Modify parameters |
| `block` | Block tool execution |
| `warn` | Allow but log warning |

---

## Step 3: Add Override Rules (If Needed)

Add rules if the tool should be replaced with a workflow in certain contexts.

### Location
```python
# server/router/application/engines/tool_override_engine.py
# In _register_default_rules() method
```

### Override Rule Structure

```python
self.register_rule(
    rule_name="tool_pattern_override",
    trigger_tool="mesh_new_tool",
    trigger_pattern="phone_like",  # Pattern that triggers override
    replacement_tools=[
        {
            "tool_name": "mesh_inset",
            "params": {"thickness": 0.03},
            "description": "Preparation step",
        },
        {
            "tool_name": "mesh_new_tool",
            "params": {},
            "inherit_params": ["offset"],  # Inherit from original call
            "description": "Main operation",
        },
    ],
)
```

### Available Patterns

| Pattern | Description | Object Shape |
|---------|-------------|--------------|
| `phone_like` | Flat rectangular | scale ~[0.4, 0.8, 0.05] |
| `tower_like` | Tall and thin | scale ~[0.3, 0.3, 2.0] |
| `box_like` | Cubic | ~equal dimensions |
| `plate_like` | Flat wide | Z much smaller than X,Y |
| `sphere_like` | Roughly spherical | ~equal dimensions |

---

## Step 4: Add Workflows (If Needed)

Create workflow files if the tool is part of larger operations.

### Location
```
server/router/application/workflows/custom/{workflow_name}.yaml
```

### Workflow Structure

```yaml
name: my_workflow
description: Description of workflow
pattern: phone_like
tags:
  - phone
  - screen
  - cutout
steps:
  - tool: mesh_inset
    params:
      thickness: 0.05
    description: Create border

  - tool: mesh_new_tool
    params:
      param1: "${param1}"  # Dynamic parameter
    description: Apply operation
```

### Dynamic Parameters

Use `${param_name}` to reference parameters passed to workflow:

```yaml
steps:
  - tool: mesh_bevel
    params:
      width: "${bevel_width}"
      segments: "${segments}"
```

---

## Step 5: Add Tests

### Unit Test for Metadata

```python
# tests/unit/router/infrastructure/test_metadata_loader.py

def test_load_new_tool_metadata(self, loader):
    """Test: new_tool metadata loads correctly."""
    metadata = loader.get_tool_metadata("mesh_new_tool")

    assert metadata is not None
    assert metadata["mode_required"] == "EDIT"
    assert metadata["selection_required"] == True
```

### Unit Test for Firewall Rule

```python
# tests/unit/router/application/test_error_firewall.py

def test_new_tool_rule(self, firewall):
    """Test: new_tool rule triggers correctly."""
    tool_call = CorrectedToolCall(
        tool_name="mesh_new_tool",
        params={"value": 100.0},
    )
    context = SceneContext(mode="OBJECT")

    result = firewall.validate(tool_call, context)

    assert result.has_violations
```

### E2E Test

```python
# tests/e2e/router/test_new_tool.py

def test_new_tool_with_router(self, router, rpc_client, clean_scene):
    """Test: new_tool processed correctly by router."""
    rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
    rpc_client.send_request("system.set_mode", {"mode": "EDIT"})
    rpc_client.send_request("mesh.select", {"action": "all"})

    tools = router.process_llm_tool_call(
        "mesh_new_tool",
        {"param1": 0.5}
    )

    assert len(tools) > 0
    assert "mesh_new_tool" in [t["tool"] for t in tools]
```

---

## Router Integration Points

### How Router Uses Tool Metadata

```
LLM Tool Call
     │
     ▼
┌────────────────────┐
│ Tool Interceptor   │ ← Validates tool_name exists
└────────────────────┘
     │
     ▼
┌────────────────────┐
│ Scene Analyzer     │ ← Gets current mode, selection
└────────────────────┘
     │
     ▼
┌────────────────────┐
│ Error Firewall     │ ← Uses mode_required, selection_required
└────────────────────┘
     │
     ▼
┌────────────────────┐
│ Tool Override      │ ← Uses patterns from metadata
└────────────────────┘
     │
     ▼
┌────────────────────┐
│ Workflow Expansion │ ← Uses related_tools, patterns
└────────────────────┘
     │
     ▼
┌────────────────────┐
│ Intent Classifier  │ ← Uses keywords, sample_prompts
└────────────────────┘
```

---

## Validation Commands

After adding tool, verify:

```bash
# 1. Metadata loads correctly
PYTHONPATH=. poetry run pytest tests/unit/router/infrastructure/test_metadata_loader.py -v -k "new_tool"

# 2. Firewall rules work
PYTHONPATH=. poetry run pytest tests/unit/router/application/test_error_firewall.py -v

# 3. Full router pipeline (if Blender running)
PYTHONPATH=. poetry run pytest tests/e2e/router/ -v -k "new_tool"
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| tool_name doesn't match MCP tool | Ensure exact match: `mesh_new_tool` |
| Missing mode_required | Add appropriate mode: OBJECT, EDIT, etc. |
| Wrong category folder | Check category enum in schema |
| Parameter range too restrictive | Allow reasonable range based on object size |
| No keywords for classifier | Add at least 3-5 relevant keywords |
| Missing sample_prompts | Add 3-5 realistic user prompts |

---

## Files Reference

| Purpose | Location |
|---------|----------|
| Metadata Schema | `server/router/infrastructure/tools_metadata/_schema.json` |
| Metadata Files | `server/router/infrastructure/tools_metadata/{category}/{tool}.json` |
| Firewall Rules | `server/router/application/engines/error_firewall.py` |
| Override Rules | `server/router/application/engines/tool_override_engine.py` |
| Workflows | `server/router/infrastructure/workflows/` |
| Metadata Loader | `server/router/infrastructure/metadata_loader.py` |
| Unit Tests | `tests/unit/router/` |
| E2E Tests | `tests/e2e/router/` |
