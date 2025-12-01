# Router Supervisor Documentation

> Intelligent Router acting as supervisor over LLM tool calls.

---

## Quick Links

| Document | Description |
|----------|-------------|
| [ROUTER_HIGH_LEVEL_OVERVIEW.md](./ROUTER_HIGH_LEVEL_OVERVIEW.md) | Concept and architecture |
| [ROUTER_ARCHITECTURE.md](./ROUTER_ARCHITECTURE.md) | Code templates and structure |
| [IMPLEMENTATION/](./IMPLEMENTATION/) | Step-by-step implementation docs |
| [WORKFLOWS/](./WORKFLOWS/) | Predefined workflow definitions |

---

## Key Concept

**Router is NOT just an "intent matcher".**

Traditional approach:
```
User → LLM → tool_call → Blender
(LLM decides everything, errors propagate)
```

New architecture:
```
User → LLM → tool_call → ROUTER → corrected_tools → Blender
                            ↑
                  [Scene Context Analyzer]
                  [Geometry Pattern Detector]
                  [Tool Correction Engine]
                  [Workflow Expansion Engine]
                  [Error Firewall]
```

---

## Components

| Component | Purpose | Status |
|-----------|---------|--------|
| **Tool Interceptor** | Capture LLM tool calls | ✅ Done |
| **Scene Context Analyzer** | Read Blender state | ✅ Done |
| **Geometry Pattern Detector** | Detect tower/phone/table patterns | ✅ Done |
| **Tool Correction Engine** | Fix params, mode, selection | ✅ Done |
| **Tool Override Engine** | Replace with better alternatives | ✅ Done |
| **Workflow Expansion Engine** | 1 tool → N tools | ✅ Done |
| **Error Firewall** | Block invalid operations | ✅ Done |
| **Intent Classifier** | Offline intent matching (LaBSE) | ✅ Done |
| **SupervisorRouter** | Main orchestrator | ✅ Done |

---

## Directory Structure

```
server/router/
├── domain/
│   ├── entities/           # Data classes (no dependencies)
│   │   ├── tool_call.py
│   │   ├── scene_context.py
│   │   └── pattern.py
│   └── interfaces/         # Abstract interfaces
│       ├── i_interceptor.py
│       ├── i_analyzer.py
│       └── i_correction_engine.py
│
├── application/
│   ├── interceptor/        # Tool interception
│   ├── analyzers/          # Scene & pattern analysis
│   ├── engines/            # Correction, override, expansion
│   ├── classifier/         # Intent classification
│   ├── workflows/          # Predefined workflows
│   └── router.py           # SupervisorRouter
│
├── infrastructure/
│   ├── metadata_loader.py  # Tool metadata loader
│   ├── config.py           # Router configuration
│   ├── logger.py           # Telemetry
│   └── tools_metadata/     # Per-tool JSON metadata (modular)
│       ├── _schema.json    # JSON Schema for validation
│       ├── scene/          # scene_*.json files
│       ├── system/         # system_*.json files
│       ├── modeling/       # modeling_*.json files
│       ├── mesh/           # mesh_*.json files
│       ├── material/       # material_*.json files
│       ├── uv/             # uv_*.json files
│       ├── curve/          # curve_*.json files
│       ├── collection/     # collection_*.json files
│       ├── lattice/        # lattice_*.json files
│       ├── sculpt/         # sculpt_*.json files
│       └── baking/         # baking_*.json files
│
└── adapters/
    └── mcp_integration.py  # Hook into MCP server
```

---

## Implementation Plan

See [TASK-039: Router Supervisor Implementation](../_TASKS/TASK-039_Router_Supervisor_Implementation.md)

### Phases

| Phase | Description | Tasks |
|-------|-------------|-------|
| **Phase 1** | Foundation & Infrastructure | 5 tasks |
| **Phase 2** | Scene Analysis | 4 tasks |
| **Phase 3** | Tool Processing Engines | 6 tasks |
| **Phase 4** | SupervisorRouter Integration | 3 tasks |
| **Phase 5** | Workflows & Patterns | 4 tasks |
| **Phase 6** | Testing & Documentation | 2 tasks |

**Total: 24 tasks**

---

## Detected Patterns

| Pattern | Detection Rule | Workflow |
|---------|---------------|----------|
| `tower_like` | height > width × 3 | Taper, subdivide |
| `phone_like` | flat, rectangular, thin | Screen cutout, bevel |
| `table_like` | flat horizontal surface | Leg extrusion |
| `pillar_like` | tall and cubic | Detail subdivisions |
| `wheel_like` | flat and circular | Spoke pattern |

---

## Example: Router in Action

**Scenario:** LLM sends `mesh_extrude` in OBJECT mode, no selection

```python
# LLM sends:
tool_call("mesh_extrude", {"depth": 0.5})

# Router detects:
# - Mode: OBJECT (mesh tool needs EDIT)
# - Selection: None (extrude needs selection)
# - Pattern: phone_like (suggests screen cutout)

# Router outputs:
[
    {"tool": "system_set_mode", "params": {"mode": "EDIT"}},
    {"tool": "mesh_select", "params": {"action": "all", "mode": "FACE"}},
    {"tool": "mesh_inset", "params": {"thickness": 0.03}},
    {"tool": "mesh_extrude", "params": {"depth": -0.02}},
    {"tool": "system_set_mode", "params": {"mode": "OBJECT"}}
]
```

**Result:** Instead of crashing, Router fixes the issues and creates a proper screen cutout!

---

## Configuration

```python
RouterConfig:
    # Correction
    auto_mode_switch: True
    auto_selection: True
    clamp_parameters: True

    # Override
    enable_overrides: True
    enable_workflow_expansion: True

    # Firewall
    block_invalid_operations: True
    auto_fix_mode_violations: True

    # Thresholds
    embedding_threshold: 0.40
    bevel_max_ratio: 0.5
    subdivide_max_cuts: 6
```

---

## See Also

- [TOOLS_ARCHITECTURE_DEEP_DIVE.md](../TOOLS_ARCHITECTURE_DEEP_DIVE.md) - Tool design philosophy
- [MESH_TOOLS_ARCHITECTURE.md](../MESH_TOOLS_ARCHITECTURE.md) - Mesh tool reference
- [MEGA_TOOLS_ARCHITECTURE.md](../MEGA_TOOLS_ARCHITECTURE.md) - Mega tool patterns
