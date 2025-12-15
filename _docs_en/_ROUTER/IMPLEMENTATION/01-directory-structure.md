# 01 - Router Directory Structure

**Task:** TASK-039-1
**Status:** ✅ Done
**Layer:** Infrastructure

---

## Overview

This task establishes the foundational directory structure for the Router Supervisor module, following Clean Architecture principles.

---

## Directory Structure

```
server/router/
├── __init__.py                    # Module entry point
│
├── domain/                        # Inner circle - no external dependencies
│   ├── __init__.py
│   ├── entities/                  # Pure data classes
│   │   └── __init__.py
│   └── interfaces/                # Abstract interfaces
│       └── __init__.py
│
├── application/                   # Middle circle - implements domain
│   ├── __init__.py
│   ├── interceptor/               # Tool interception (TASK-039-6)
│   │   └── __init__.py
│   ├── analyzers/                 # Scene & pattern analysis (TASK-039-7,8,9)
│   │   └── __init__.py
│   ├── engines/                   # Processing engines (TASK-039-10-14)
│   │   └── __init__.py
│   ├── classifier/                # Intent classification (TASK-039-15)
│   │   └── __init__.py
│   ├── workflows/                 # Predefined workflows (TASK-039-19-22)
│   │   └── __init__.py
│   └── router.py                  # SupervisorRouter (TASK-039-16)
│
├── infrastructure/                # Outer circle - frameworks, config
│   ├── __init__.py
│   ├── config.py                  # RouterConfig dataclass
│   ├── metadata_loader.py         # Tool metadata loading (TASK-039-4)
│   ├── logger.py                  # Telemetry (TASK-039-18)
│   └── tools_metadata/            # Per-tool JSON metadata
│       ├── _schema.json           # JSON Schema for validation
│       ├── scene/
│       ├── system/
│       ├── modeling/
│       ├── mesh/
│       ├── material/
│       ├── uv/
│       ├── curve/
│       ├── collection/
│       ├── lattice/
│       ├── sculpt/
│       └── baking/
│
└── adapters/                      # Interface adapters
    ├── __init__.py
    └── mcp_integration.py         # MCP server hook (TASK-039-17)
```

---

## Clean Architecture Layers

### Domain Layer (`domain/`)

- **Purpose:** Core business logic and contracts
- **Dependencies:** None (pure Python only)
- **Contents:**
  - `entities/` - Data classes (InterceptedToolCall, SceneContext, etc.)
  - `interfaces/` - Abstract base classes for all components

### Application Layer (`application/`)

- **Purpose:** Use cases and implementations
- **Dependencies:** Domain layer only
- **Contents:**
  - `interceptor/` - Captures LLM tool calls
  - `analyzers/` - Scene context and pattern detection
  - `engines/` - Correction, override, expansion, firewall
  - `classifier/` - Intent classification (LaBSE)
  - `workflows/` - Predefined modeling workflows
  - `router.py` - Main orchestrator

### Infrastructure Layer (`infrastructure/`)

- **Purpose:** External concerns (config, logging, data loading)
- **Dependencies:** Application and Domain layers
- **Contents:**
  - `config.py` - RouterConfig settings
  - `metadata_loader.py` - JSON metadata loading
  - `logger.py` - Decision logging and telemetry
  - `tools_metadata/` - Per-tool JSON files

### Adapters Layer (`adapters/`)

- **Purpose:** Interface with external systems
- **Dependencies:** All layers
- **Contents:**
  - `mcp_integration.py` - Hook into MCP server

---

## Key Files Created

| File | Purpose |
|------|---------|
| `config.py` | RouterConfig dataclass with all settings |
| `metadata_loader.py` | Placeholder for metadata loading |
| `logger.py` | Placeholder for telemetry |
| `router.py` | SupervisorRouter placeholder |
| `mcp_integration.py` | MCP integration placeholder |
| `_schema.json` | JSON Schema for tool metadata |

---

## Usage

```python
from server.router import RouterConfig
from server.router.application.router import SupervisorRouter

# Create router with default config
router = SupervisorRouter()

# Or with custom config
config = RouterConfig(
    auto_mode_switch=True,
    embedding_threshold=0.5
)
router = SupervisorRouter(config)
```

---

## Next Steps

- **TASK-039-2:** Implement domain entities
- **TASK-039-3:** Define domain interfaces
- **TASK-039-4:** Implement metadata loader
- **TASK-039-5:** Complete router configuration

---

## See Also

- [ROUTER_HIGH_LEVEL_OVERVIEW.md](../ROUTER_HIGH_LEVEL_OVERVIEW.md)
- [ROUTER_ARCHITECTURE.md](../ROUTER_ARCHITECTURE.md)
- [TASK-039](../../_TASKS/TASK-039_Router_Supervisor_Implementation.md)
