# 23. YAML Workflow Integration & Router Tools Clean Architecture

**Task:** TASK-041 (Phase -1, P0)
**Date:** 2025-12-02
**Status:** Completed

---

## Overview

This implementation connects YAML-based workflows to the Router Supervisor system and adds Clean Architecture pattern to router tools.

---

## Problem Statement

Before this implementation:
1. `WorkflowLoader` parsed YAML/JSON files but results were not used
2. `WorkflowRegistry` had workflows but `WorkflowExpansionEngine` used its own hardcoded `PREDEFINED_WORKFLOWS`
3. Router had no way to know what user was building (no goal tracking)
4. Router tools were not following Clean Architecture pattern

---

## Solution Architecture

### Clean Architecture Pattern for Router Tools

```
┌─────────────────────────────────────────────────────────────┐
│ 1. DOMAIN LAYER                                             │
│    server/domain/tools/router.py                            │
│    - IRouterTool interface                                  │
├─────────────────────────────────────────────────────────────┤
│ 2. APPLICATION LAYER                                        │
│    server/application/tool_handlers/router_handler.py       │
│    - RouterToolHandler implementation                       │
├─────────────────────────────────────────────────────────────┤
│ 3. INFRASTRUCTURE LAYER                                     │
│    server/infrastructure/di.py                              │
│    - get_router_handler() provider                          │
├─────────────────────────────────────────────────────────────┤
│ 4. ADAPTER LAYER                                            │
│    server/adapters/mcp/areas/router.py                      │
│    - @mcp.tool() decorated functions                        │
└─────────────────────────────────────────────────────────────┘
```

### YAML Workflow Integration

```
┌────────────────────────────────────────────────────────────────┐
│          SupervisorRouter                                       │
│    + set_current_goal()                                        │
│    + get_current_goal()                                        │
│    + get_pending_workflow()                                    │
└────────────────────┬───────────────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────────────┐
│     WorkflowExpansionEngine                                     │
│  ┌─────────────────────────────────────────────────────┐       │
│  │      Uses WorkflowRegistry (not hardcoded dict!)    │       │
│  └─────────────────────────────────────────────────────┘       │
└────────────────────┬───────────────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────────────┐
│       WorkflowRegistry                                          │
│  - Built-in workflows (Python)                                 │
│  - Custom workflows (YAML) via load_custom_workflows()         │
│  - ensure_custom_loaded() for lazy loading                     │
└────────────────────┬───────────────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────────────┐
│        WorkflowLoader                                           │
│   (loads YAML from workflows/custom/)                          │
└────────────────────────────────────────────────────────────────┘
```

---

## Files Created

### Domain Layer

**`server/domain/tools/router.py`**

```python
class IRouterTool(ABC):
    @abstractmethod
    def set_goal(self, goal: str) -> str:
        """Set current modeling goal."""
        pass

    @abstractmethod
    def get_status(self) -> str:
        """Get router status and statistics."""
        pass

    @abstractmethod
    def clear_goal(self) -> str:
        """Clear current goal."""
        pass

    @abstractmethod
    def get_goal(self) -> Optional[str]:
        """Get current goal."""
        pass

    @abstractmethod
    def get_pending_workflow(self) -> Optional[str]:
        """Get workflow matched from goal."""
        pass

    @abstractmethod
    def is_enabled(self) -> bool:
        """Check if router is enabled."""
        pass
```

### Application Layer

**`server/application/tool_handlers/router_handler.py`**

```python
class RouterToolHandler(IRouterTool):
    def __init__(self, router=None, enabled: bool = True):
        self._router = router
        self._enabled = enabled

    def _get_router(self):
        if self._router is None:
            from server.infrastructure.di import get_router
            self._router = get_router()
        return self._router

    def set_goal(self, goal: str) -> str:
        if not self._enabled:
            return "Router is disabled..."
        router = self._get_router()
        matched_workflow = router.set_current_goal(goal)
        # ... format response
```

### WorkflowTriggerer

**`server/router/application/triggerer/workflow_triggerer.py`**

```python
class WorkflowTriggerer:
    """Determines when to trigger workflows.

    Uses multiple sources:
    1. Explicit goal (highest priority) - set via router_set_goal
    2. Keyword matching from goal
    3. Tool-based heuristics (fallback)
    4. Pattern-based detection (fallback)
    """

    def set_explicit_goal(self, goal: str) -> Optional[str]:
        """Set explicit modeling goal and find matching workflow."""
        self._explicit_goal = goal
        registry = self._get_registry()
        workflow_name = registry.find_by_keywords(goal)
        # ...

    def _heuristic_flat_cube(self, params, context) -> Optional[str]:
        """Detect phone/tablet from flat cube creation."""
        if context.proportions and context.proportions.is_flat:
            return "phone_workflow"
        return None

    def _heuristic_tall_scale(self, params, context) -> Optional[str]:
        """Detect tower from tall scale transformation."""
        scale = params.get("scale")
        if scale and len(scale) >= 3:
            x, y, z = scale[0], scale[1], scale[2]
            if z > 3 * max(x, y):
                return "tower_workflow"
        return None
```

---

## Files Modified

### WorkflowRegistry

**`server/router/application/workflows/registry.py`**

Added:
```python
def load_custom_workflows(self, reload: bool = False) -> int:
    """Load custom workflows from YAML files."""
    if self._custom_loaded and not reload:
        return 0
    loader = get_workflow_loader()
    workflows = loader.load_all()
    for name, definition in workflows.items():
        self.register_definition(definition)
    self._custom_loaded = True
    return count

def ensure_custom_loaded(self) -> None:
    """Ensure custom workflows are loaded (lazy loading)."""
    if not self._custom_loaded:
        self.load_custom_workflows()
```

### WorkflowExpansionEngine

**`server/router/application/engines/workflow_expansion_engine.py`**

Changed:
- Removed `PREDEFINED_WORKFLOWS` dict
- Added `_get_registry()` for lazy loading
- All methods now delegate to WorkflowRegistry

```python
def _get_registry(self):
    if self._registry is None:
        from server.router.application.workflows.registry import get_workflow_registry
        self._registry = get_workflow_registry()
        self._registry.ensure_custom_loaded()
    return self._registry

def get_workflow(self, workflow_name: str):
    registry = self._get_registry()
    definition = registry.get_definition(workflow_name)
    if definition:
        return [step.to_dict() for step in definition.steps]
    return None
```

### SupervisorRouter

**`server/router/application/router.py`**

Added goal tracking:
```python
def __init__(self, ...):
    self._current_goal: Optional[str] = None
    self._pending_workflow: Optional[str] = None

def set_current_goal(self, goal: str) -> Optional[str]:
    self._current_goal = goal
    registry = get_workflow_registry()
    registry.ensure_custom_loaded()
    workflow_name = registry.find_by_keywords(goal)
    if workflow_name:
        self._pending_workflow = workflow_name
    return workflow_name

def get_current_goal(self) -> Optional[str]:
    return self._current_goal

def get_pending_workflow(self) -> Optional[str]:
    return self._pending_workflow

def clear_goal(self) -> None:
    self._current_goal = None
    self._pending_workflow = None
```

---

## MCP Tools

### router_set_goal

```python
@mcp.tool()
def router_set_goal(ctx: Context, goal: str) -> str:
    """
    [SYSTEM][CRITICAL] Tell the Router what you're building.

    IMPORTANT: Call this FIRST before ANY modeling operation!

    Args:
        goal: What you're creating (e.g., "smartphone", "table")

    Supported keywords:
        - phone, smartphone, tablet -> phone_workflow
        - tower, pillar, column -> tower_workflow
        - table, desk -> table_workflow
    """
    handler = get_router_handler()
    return handler.set_goal(goal)
```

### router_get_status

```python
@mcp.tool()
def router_get_status(ctx: Context) -> str:
    """[SYSTEM][SAFE] Get current Router Supervisor status."""
    handler = get_router_handler()
    return handler.get_status()
```

### router_clear_goal

```python
@mcp.tool()
def router_clear_goal(ctx: Context) -> str:
    """[SYSTEM][SAFE] Clear the current modeling goal."""
    handler = get_router_handler()
    return handler.clear_goal()
```

---

## DI Registration

**`server/infrastructure/di.py`**

```python
from server.application.tool_handlers.router_handler import RouterToolHandler
from server.domain.tools.router import IRouterTool

_router_handler_instance = None

def get_router_handler() -> IRouterTool:
    """Provider for IRouterTool. Singleton with lazy initialization."""
    global _router_handler_instance
    if _router_handler_instance is None:
        config = get_config()
        _router_handler_instance = RouterToolHandler(
            router=get_router() if config.ROUTER_ENABLED else None,
            enabled=config.ROUTER_ENABLED,
        )
    return _router_handler_instance
```

---

## Testing

All 561 router tests pass after refactoring.

Key test updates:
- Removed `PREDEFINED_WORKFLOWS` imports from tests
- Updated tests to use `WorkflowRegistry` directly
- Added integration tests for YAML workflow loading

---

## Usage Example

```python
# LLM workflow:

# 1. Set goal first
router_set_goal("smartphone")
# -> "Goal set: 'smartphone'\nMatched workflow: phone_workflow\n..."

# 2. Create primitive (router knows it's for a phone)
modeling_create_primitive("CUBE")
# -> Router can now expand to phone workflow

# 3. Check status
router_get_status()
# -> Shows current goal, pending workflow, stats

# 4. Clear goal when done
router_clear_goal()
# -> "Goal cleared. Ready for new modeling task."
```

---

## Next Steps (TASK-041 Remaining)

- **Phase 1 (P1):** Integrate WorkflowTriggerer into SupervisorRouter pipeline
- **Phase 2 (P2):** Expression Evaluator for `$CALCULATE(...)`
- **Phase 3 (P3):** Condition Evaluator for step conditions
- **Phase 4 (P4):** Proportion Resolver for `$AUTO_*` params
