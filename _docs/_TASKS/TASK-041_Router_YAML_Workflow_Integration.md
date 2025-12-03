# TASK-041: Router YAML Workflow Integration

**Status:** 🟡 In Progress (Phase -1, P0, P1, P2 ✅)
**Priority:** 🔴 High
**Category:** Router Enhancement
**Estimated Sub-Tasks:** 18
**Parent Task:** TASK-039 (Router Supervisor Implementation)
**Created:** 2025-12-02

---

## Overview

Integrate YAML-based custom workflows into the Router Supervisor system. Currently, the router has separate components that are not connected:

1. **WorkflowLoader** - parses YAML/JSON workflows ✅
2. **WorkflowRegistry** - central workflow registry ✅
3. **WorkflowExpansionEngine** - expands tools to workflows (uses its OWN hardcoded workflows, ignores Registry!)

**Problem:** YAML workflows are parsed but NOT used by the router. Also missing:
- Dynamic parameters (`$CALCULATE(...)`)
- Conditional step execution (`condition: "..."`)
- Auto-triggering workflows based on user prompts

---

## Current Architecture Gap

```
                    ┌──────────────────────────────────────┐
                    │          SupervisorRouter            │
                    └────────────────┬─────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────┐
                    │     WorkflowExpansionEngine          │
                    │  ┌─────────────────────────────┐     │
                    │  │   PREDEFINED_WORKFLOWS      │     │  ← Hardcoded dict
                    │  │   (ignores Registry!)       │     │
                    │  └─────────────────────────────┘     │
                    └──────────────────────────────────────┘

    ┌────────────────────┐          ┌─────────────────────┐
    │   WorkflowLoader   │          │   WorkflowRegistry   │
    │   (parses YAML)    │────X────▶│   (has find_by_*)   │
    └────────────────────┘          └─────────────────────┘
              │                              │
              ▼                              X (not used)
    workflows/custom/*.yaml
```

**Target Architecture:**

```
                    ┌──────────────────────────────────────┐
                    │          SupervisorRouter            │
                    │    + WorkflowTriggerer component     │
                    └────────────────┬─────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────┐
                    │     WorkflowExpansionEngine          │
                    │  ┌─────────────────────────────┐     │
                    │  │      WorkflowRegistry       │────────▶ find_by_keywords()
                    │  │   (unified source)          │────────▶ find_by_pattern()
                    │  └─────────────────────────────┘     │
                    └──────────────────────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────┐
                    │       WorkflowRegistry               │
                    │  - Built-in workflows (Python)       │
                    │  - Custom workflows (YAML)           │
                    │  - ConditionEvaluator                │
                    │  - ExpressionEvaluator               │
                    └────────────────┬─────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────┐
                    │        WorkflowLoader                │
                    │   (loads YAML at startup)            │
                    └──────────────────────────────────────┘
```

---

## Phase -1: Intent Source (PREREQUISITE)

**Problem:** Router has no access to the original user prompt. FastMCP `Context` does not expose conversation history.

**Solution:** Dedicated MCP tool `router_set_goal` + heuristics as fallback.

### TASK-041-0: Create `router_set_goal` MCP Tool

**Priority:** 🔴 Critical (PREREQUISITE)
**Layer:** Adapters (MCP)
**Estimated Time:** 1h

**Problem:** Router doesn't know what the user wants to build. LLM calls `modeling_create_primitive(CUBE)` but router doesn't know if it's a phone, house, or table.

**Solution:** Add a tool that LLM **MUST** call first when modeling.

**Files to Create/Modify:**

| File | Change |
|------|--------|
| `server/adapters/mcp/areas/router.py` | **NEW** - router tools (set_goal, get_status) |
| `server/router/application/router.py` | Add `set_current_goal()`, `get_current_goal()` |
| `server/adapters/mcp/instance.py` | Import router area |

**Code:**

```python
# server/adapters/mcp/areas/router.py

from typing import Optional
from fastmcp import Context
from server.adapters.mcp.instance import mcp
from server.infrastructure.di import get_router, is_router_enabled


@mcp.tool()
def router_set_goal(ctx: Context, goal: str) -> str:
    """
    🎯 [SYSTEM][CRITICAL] Tell the Router what you're building.

    ⚠️  IMPORTANT: Call this FIRST before ANY modeling operation!

    The Router Supervisor uses this to optimize your workflow automatically.
    Without setting a goal, the router cannot help you with smart workflow
    expansion and error prevention.

    Args:
        goal: What you're creating. Be specific!
              Examples: "smartphone", "wooden table", "medieval tower",
                       "office chair", "sports car", "human face"

    Returns:
        Confirmation with matched workflow (if any).

    Example workflow:
        1. router_set_goal("smartphone")     # ← FIRST!
        2. modeling_create_primitive("CUBE") # Router expands to phone workflow
        3. ... router handles the rest automatically

    Supported goal keywords (trigger workflows):
        - phone, smartphone, tablet, mobile → phone_workflow
        - tower, pillar, column, obelisk → tower_workflow
        - table, desk, surface → table_workflow
        - house, building, dom → house_workflow
        - chair, seat, stool → chair_workflow
    """
    if not is_router_enabled():
        return "Router is disabled. Goal noted but no workflow optimization available."

    router = get_router()
    if router is None:
        return "Router not initialized."

    # Set goal and find matching workflow
    matched_workflow = router.set_current_goal(goal)

    if matched_workflow:
        ctx.info(f"[ROUTER] Goal set: {goal} → workflow: {matched_workflow}")
        return f"✅ Goal set: '{goal}'\n🔄 Matched workflow: {matched_workflow}\n\nProceeding with your next tool call will trigger this workflow automatically."
    else:
        ctx.info(f"[ROUTER] Goal set: {goal} (no matching workflow)")
        return f"✅ Goal set: '{goal}'\n⚠️ No specific workflow matched. Router will use heuristics to assist.\n\nYou can proceed with modeling - router will still help with mode switching and error prevention."


@mcp.tool()
def router_get_status(ctx: Context) -> str:
    """
    [SYSTEM][SAFE] Get current Router Supervisor status.

    Returns information about:
    - Current goal (if set)
    - Pending workflow
    - Router statistics
    - Component status
    """
    if not is_router_enabled():
        return "Router Supervisor is DISABLED.\nSet ROUTER_ENABLED=true to enable."

    router = get_router()
    if router is None:
        return "Router not initialized."

    goal = router.get_current_goal()
    stats = router.get_stats()
    components = router.get_component_status()

    lines = [
        "=== Router Supervisor Status ===",
        f"Current goal: {goal or '(not set)'}",
        f"Pending workflow: {router.get_pending_workflow() or '(none)'}",
        "",
        "Statistics:",
        f"  Total calls processed: {stats.get('total_calls', 0)}",
        f"  Corrections applied: {stats.get('corrections_applied', 0)}",
        f"  Workflows expanded: {stats.get('workflows_expanded', 0)}",
        f"  Blocked calls: {stats.get('blocked_calls', 0)}",
    ]

    return "\n".join(lines)
```

**Router Changes:**

```python
# server/router/application/router.py

class SupervisorRouter:
    def __init__(self, ...):
        # ... existing ...
        self._current_goal: Optional[str] = None
        self._pending_workflow: Optional[str] = None

    def set_current_goal(self, goal: str) -> Optional[str]:
        """Set current modeling goal and find matching workflow.

        Args:
            goal: User's modeling goal (e.g., "smartphone", "table")

        Returns:
            Name of matched workflow, or None.
        """
        self._current_goal = goal

        # Try to find matching workflow
        from server.router.application.workflows.registry import get_workflow_registry
        registry = get_workflow_registry()
        registry.ensure_custom_loaded()

        workflow_name = registry.find_by_keywords(goal)
        if workflow_name:
            self._pending_workflow = workflow_name
            self.logger.log_info(f"Goal '{goal}' matched workflow: {workflow_name}")

        return workflow_name

    def get_current_goal(self) -> Optional[str]:
        """Get current modeling goal."""
        return self._current_goal

    def get_pending_workflow(self) -> Optional[str]:
        """Get pending workflow (set by goal)."""
        return self._pending_workflow

    def clear_goal(self) -> None:
        """Clear current goal (after workflow completion)."""
        self._current_goal = None
        self._pending_workflow = None
```

**Docstring Strategy (forcing usage):**

Tool docstring contains:
1. `🎯 [SYSTEM][CRITICAL]` - visual highlighting
2. `⚠️ IMPORTANT: Call this FIRST` - clear instruction
3. `Example workflow:` - shows order of operations
4. `Supported goal keywords` - list of keywords

**Tests:**
- `tests/unit/router/test_router_set_goal.py`
- `tests/e2e/router/test_goal_workflow_trigger.py`

**Acceptance Criteria:**
- [x] `router_set_goal("phone")` sets goal and finds `phone_workflow`
- [x] `router_get_status()` shows current goal
- [x] LLM receives clear feedback about matched workflow
- [x] Goal persists across subsequent tool calls in session

---

### TASK-041-0b: Add Heuristics Fallback

**Priority:** 🟡 Medium (PREREQUISITE)
**Layer:** Application
**Estimated Time:** 1h

**Problem:** If LLM doesn't call `router_set_goal`, router should try to guess.

**Files to Modify:**

| File | Change |
|------|--------|
| `server/router/application/triggerer/workflow_triggerer.py` | Add `_check_heuristic_trigger()` |

**Heuristics:**

```python
# In WorkflowTriggerer

TOOL_HEURISTICS = {
    "modeling_create_primitive": {
        # If creating CUBE with flat scale params → might be phone/tablet
        "CUBE": lambda params: "phone_workflow" if _is_flat_scale(params) else None,
    },
}

def _check_heuristic_trigger(
    self,
    tool_name: str,
    params: Dict[str, Any],
    context: SceneContext,
) -> Optional[str]:
    """Guess workflow based on tool + params + context."""

    # Check tool-specific heuristics
    if tool_name in self.TOOL_HEURISTICS:
        tool_heuristics = self.TOOL_HEURISTICS[tool_name]
        # ... apply heuristics ...

    # Check scene proportions
    if context.proportions:
        if context.proportions.is_flat:
            # Flat object being edited → might be phone/tablet
            pass

    return None
```

**Note:** Heuristics are a fallback - not ideal, but better than nothing.

---

## Phase 0: Connect YAML Workflows (P0)

### TASK-041-1: Integrate WorkflowLoader with WorkflowRegistry

**Priority:** 🔴 High (P0)
**Layer:** Infrastructure → Application
**Estimated Time:** 1h

**Problem:** `WorkflowLoader` parses YAML, but results do NOT reach `WorkflowRegistry`.

**Files to Modify:**

| File | Change |
|------|--------|
| `server/router/application/workflows/registry.py` | Add `load_custom_workflows()` method |
| `server/router/infrastructure/workflow_loader.py` | Add `get_as_definitions()` method |

**Code Changes:**

```python
# server/router/application/workflows/registry.py

from server.router.infrastructure.workflow_loader import get_workflow_loader

class WorkflowRegistry:
    def __init__(self):
        # ... existing ...
        self._custom_loaded = False

    def load_custom_workflows(self, reload: bool = False) -> int:
        """Load custom workflows from YAML files.

        Args:
            reload: Force reload even if already loaded.

        Returns:
            Number of workflows loaded.
        """
        if self._custom_loaded and not reload:
            return 0

        loader = get_workflow_loader()
        workflows = loader.load_all()

        count = 0
        for name, definition in workflows.items():
            self.register_definition(definition)
            count += 1

        self._custom_loaded = True
        return count

    def ensure_custom_loaded(self) -> None:
        """Ensure custom workflows are loaded (lazy loading)."""
        if not self._custom_loaded:
            self.load_custom_workflows()
```

**Tests:**
- `tests/unit/router/workflows/test_registry_yaml_integration.py`

**Acceptance Criteria:**
- [x] `WorkflowRegistry.load_custom_workflows()` loads all YAML from `workflows/custom/`
- [x] `find_by_keywords("table")` returns `"table_workflow"` from YAML
- [x] YAML workflows are available via `expand_workflow()`

---

### TASK-041-2: Wire WorkflowRegistry into WorkflowExpansionEngine

**Priority:** 🔴 High (P0)
**Layer:** Application
**Estimated Time:** 1h

**Problem:** `WorkflowExpansionEngine` has its own `PREDEFINED_WORKFLOWS` dict and ignores `WorkflowRegistry`.

**Files to Modify:**

| File | Change |
|------|--------|
| `server/router/application/engines/workflow_expansion_engine.py` | Use `WorkflowRegistry` instead of internal dict |

**Code Changes:**

```python
# server/router/application/engines/workflow_expansion_engine.py

from server.router.application.workflows.registry import get_workflow_registry

class WorkflowExpansionEngine(IExpansionEngine):
    def __init__(self, config: Optional[RouterConfig] = None):
        self._config = config or RouterConfig()
        self._registry = get_workflow_registry()
        # Ensure custom workflows are loaded
        self._registry.ensure_custom_loaded()

    def expand(
        self,
        tool_name: str,
        params: Dict[str, Any],
        context: SceneContext,
        pattern: Optional[DetectedPattern] = None,
    ) -> Optional[List[CorrectedToolCall]]:
        if not self._config.enable_workflow_expansion:
            return None

        # Check if pattern suggests a workflow
        if pattern and pattern.suggested_workflow:
            workflow_name = self._registry.find_by_pattern(pattern.name)
            if workflow_name:
                return self._registry.expand_workflow(workflow_name, params)

        return None

    def get_workflow(self, workflow_name: str) -> Optional[List[Dict[str, Any]]]:
        """Get workflow steps by name."""
        definition = self._registry.get_definition(workflow_name)
        if definition:
            return [step.to_dict() for step in definition.steps]
        return None

    def register_workflow(self, name: str, steps: List[Dict[str, Any]], ...) -> None:
        """Register a new workflow (delegates to registry)."""
        # Convert to WorkflowDefinition and register
        definition = WorkflowDefinition(
            name=name,
            description=f"Custom workflow: {name}",
            steps=[WorkflowStep(**s) for s in steps],
            trigger_pattern=trigger_pattern,
            trigger_keywords=trigger_keywords or [],
        )
        self._registry.register_definition(definition)

    def get_available_workflows(self) -> List[str]:
        """Get all available workflow names."""
        return self._registry.get_all_workflows()

    # REMOVE: PREDEFINED_WORKFLOWS dict
    # REMOVE: _workflows instance variable
```

**Tests:**
- Update `tests/unit/router/application/test_workflow_expansion_engine.py`

**Acceptance Criteria:**
- [x] `WorkflowExpansionEngine` uses `WorkflowRegistry` as single source
- [x] Old `PREDEFINED_WORKFLOWS` dict removed
- [x] All existing tests pass with new implementation

---

### TASK-041-3: Auto-load YAML Workflows on Router Startup

**Priority:** 🔴 High (P0)
**Layer:** Application
**Estimated Time:** 30min

**Files to Modify:**

| File | Change |
|------|--------|
| `server/router/application/router.py` | Load custom workflows on init |
| `server/router/infrastructure/workflow_loader.py` | Add directory creation if missing |

**Code Changes:**

```python
# server/router/application/router.py

class SupervisorRouter:
    def __init__(self, ...):
        # ... existing init ...

        # Load custom workflows
        self._load_custom_workflows()

    def _load_custom_workflows(self) -> None:
        """Load custom workflows from YAML files."""
        from server.router.application.workflows.registry import get_workflow_registry

        registry = get_workflow_registry()
        count = registry.load_custom_workflows()

        if count > 0:
            self.logger.log_info(f"Loaded {count} custom workflows from YAML")
```

```python
# server/router/infrastructure/workflow_loader.py

class WorkflowLoader:
    def load_all(self) -> Dict[str, WorkflowDefinition]:
        # Create directory if doesn't exist
        if not self._workflows_dir.exists():
            self._workflows_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created workflows directory: {self._workflows_dir}")
            return {}
        # ... rest of existing code ...
```

**Acceptance Criteria:**
- [x] Router loads YAML workflows automatically on startup
- [x] Missing `workflows/custom/` directory is created
- [x] Log message shows number of loaded workflows

---

## Phase 1: Auto-Triggering Workflows (P1) ✅

### TASK-041-4: Create WorkflowTriggerer Component

**Priority:** 🔴 High (P1)
**Layer:** Application
**Estimated Time:** 2h

**Problem:** Currently workflows are only triggered by pattern detection. We need to trigger based on:
1. User prompt keywords
2. First tool in sequence (e.g., `modeling_create_primitive` → check if workflow applies)

**Files to Create:**

| File | Purpose |
|------|---------|
| `server/router/application/triggerer/workflow_triggerer.py` | Main triggerer component |
| `server/router/application/triggerer/__init__.py` | Module init |
| `server/router/domain/interfaces/i_workflow_triggerer.py` | Interface |

**Code:**

```python
# server/router/domain/interfaces/i_workflow_triggerer.py

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

class IWorkflowTriggerer(ABC):
    @abstractmethod
    def check_trigger(
        self,
        tool_name: str,
        params: Dict[str, Any],
        prompt: Optional[str],
        context: Any,
    ) -> Optional[str]:
        """Check if a workflow should be triggered.

        Args:
            tool_name: Tool being called.
            params: Tool parameters.
            prompt: Original user prompt (if available).
            context: Scene context.

        Returns:
            Workflow name to trigger, or None.
        """
        pass
```

```python
# server/router/application/triggerer/workflow_triggerer.py

from typing import Optional, Dict, Any
import logging

from server.router.domain.interfaces.i_workflow_triggerer import IWorkflowTriggerer
from server.router.application.workflows.registry import get_workflow_registry
from server.router.domain.entities.scene_context import SceneContext
from server.router.domain.entities.pattern import DetectedPattern
from server.router.infrastructure.config import RouterConfig

logger = logging.getLogger(__name__)


class WorkflowTriggerer(IWorkflowTriggerer):
    """Determines when to trigger workflows based on context.

    Trigger priority:
    1. Prompt keywords (highest)
    2. Detected pattern
    3. Tool-specific rules (lowest)
    """

    # Tools that can start a workflow
    WORKFLOW_STARTER_TOOLS = [
        "modeling_create_primitive",
        "scene_create",
    ]

    def __init__(self, config: Optional[RouterConfig] = None):
        self._config = config or RouterConfig()
        self._registry = get_workflow_registry()
        self._registry.ensure_custom_loaded()

    def check_trigger(
        self,
        tool_name: str,
        params: Dict[str, Any],
        prompt: Optional[str],
        context: SceneContext,
        pattern: Optional[DetectedPattern] = None,
    ) -> Optional[str]:
        """Check if workflow should be triggered."""

        # 1. Check prompt keywords (highest priority)
        if prompt:
            workflow_name = self._check_prompt_trigger(prompt)
            if workflow_name:
                logger.info(f"[ROUTER] Workflow triggered by prompt: {workflow_name}")
                return workflow_name

        # 2. Check pattern trigger
        if pattern:
            workflow_name = self._check_pattern_trigger(pattern)
            if workflow_name:
                logger.info(f"[ROUTER] Workflow triggered by pattern: {workflow_name}")
                return workflow_name

        # 3. Check tool-specific trigger
        if tool_name in self.WORKFLOW_STARTER_TOOLS:
            workflow_name = self._check_tool_trigger(tool_name, params)
            if workflow_name:
                logger.info(f"[ROUTER] Workflow triggered by tool: {workflow_name}")
                return workflow_name

        return None

    def _check_prompt_trigger(self, prompt: str) -> Optional[str]:
        """Check if prompt keywords match a workflow."""
        return self._registry.find_by_keywords(prompt)

    def _check_pattern_trigger(self, pattern: DetectedPattern) -> Optional[str]:
        """Check if pattern matches a workflow."""
        return self._registry.find_by_pattern(pattern.name)

    def _check_tool_trigger(
        self,
        tool_name: str,
        params: Dict[str, Any],
    ) -> Optional[str]:
        """Check if tool+params suggest a workflow.

        Example: modeling_create_primitive(CUBE) with flat proportions → phone_workflow
        """
        # Future: heuristics based on tool params
        return None
```

**Tests:**
- `tests/unit/router/application/test_workflow_triggerer.py`

**Acceptance Criteria:**
- [x] `WorkflowTriggerer` checks prompt keywords first
- [x] Falls back to pattern matching
- [x] Integrates with `WorkflowRegistry.find_by_keywords()`

---

### TASK-041-5: Integrate WorkflowTriggerer into SupervisorRouter ✅

**Priority:** 🔴 High (P1)
**Layer:** Application
**Estimated Time:** 1h

**Files to Modify:**

| File | Change |
|------|--------|
| `server/router/application/router.py` | Add WorkflowTriggerer, call in pipeline |

**Code Changes:**

```python
# server/router/application/router.py

from server.router.application.triggerer.workflow_triggerer import WorkflowTriggerer

class SupervisorRouter:
    def __init__(self, ...):
        # ... existing ...
        self.triggerer = WorkflowTriggerer(config=self.config)

    def process_llm_tool_call(
        self,
        tool_name: str,
        params: Dict[str, Any],
        prompt: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        # ... existing steps 1-4 ...

        # Step 5: Check workflow trigger (NEW - before override)
        triggered_workflow = self._check_workflow_trigger(
            tool_name, params, prompt, context, pattern
        )

        # Step 6: Override - skip if workflow triggered
        override_result = None
        if not triggered_workflow:
            override_result = self._check_override(tool_name, params, context, pattern)

        # Step 7: Expand workflow
        expanded = None
        if triggered_workflow:
            expanded = self._expand_triggered_workflow(triggered_workflow, params)
        elif not override_result:
            expanded = self._expand_workflow(tool_name, params, context, pattern)

        # ... rest of pipeline ...

    def _check_workflow_trigger(
        self,
        tool_name: str,
        params: Dict[str, Any],
        prompt: Optional[str],
        context: SceneContext,
        pattern: Optional[DetectedPattern],
    ) -> Optional[str]:
        """Check if workflow should be triggered."""
        if not self.config.enable_workflow_expansion:
            return None

        return self.triggerer.check_trigger(
            tool_name, params, prompt, context, pattern
        )

    def _expand_triggered_workflow(
        self,
        workflow_name: str,
        params: Dict[str, Any],
    ) -> List[CorrectedToolCall]:
        """Expand a triggered workflow."""
        from server.router.application.workflows.registry import get_workflow_registry

        registry = get_workflow_registry()
        calls = registry.expand_workflow(workflow_name, params)

        if calls:
            self._processing_stats["workflows_expanded"] += 1
            self.logger.log_workflow_triggered(workflow_name, len(calls))

        return calls
```

**Acceptance Criteria:**
- [x] Workflow triggering happens before override check
- [x] Triggered workflows bypass override engine
- [x] Logging shows workflow trigger reason

---

### TASK-041-6: Add Workflow Trigger Logging ✅

**Priority:** 🟡 Medium (P1)
**Layer:** Infrastructure
**Estimated Time:** 30min

**Files to Modify:**

| File | Change |
|------|--------|
| `server/router/infrastructure/logger.py` | Add `log_workflow_triggered()` method |

**Code:**

```python
# server/router/infrastructure/logger.py

class RouterLogger:
    def log_workflow_triggered(
        self,
        workflow_name: str,
        step_count: int,
        trigger_reason: str = "keyword",
    ) -> None:
        """Log workflow trigger event."""
        self._log(
            "INFO",
            f"[ROUTER] Workflow triggered: {workflow_name} ({step_count} steps) - reason: {trigger_reason}"
        )
```

---

## Phase 2: Expression Evaluator (P2) ✅

### TASK-041-7: Create Expression Evaluator ✅

**Priority:** 🟡 Medium (P2)
**Layer:** Application
**Estimated Time:** 2h

**Purpose:** Evaluate `$CALCULATE(...)` expressions in workflow params.

**Files to Create:**

| File | Purpose |
|------|---------|
| `server/router/application/evaluator/expression_evaluator.py` | Safe expression evaluator |
| `server/router/application/evaluator/__init__.py` | Module init |

**Code:**

```python
# server/router/application/evaluator/expression_evaluator.py

import re
import math
import operator
from typing import Dict, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


class ExpressionEvaluator:
    """Safe expression evaluator for workflow parameters.

    Supports:
    - Basic arithmetic: +, -, *, /, **
    - Math functions: abs, min, max, round, floor, ceil
    - Variable references: width, height, depth, etc.

    Does NOT support:
    - Arbitrary Python code
    - Imports
    - Function calls beyond whitelist
    """

    # Allowed operators
    OPERATORS = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
        '**': operator.pow,
        '%': operator.mod,
    }

    # Allowed functions
    FUNCTIONS = {
        'abs': abs,
        'min': min,
        'max': max,
        'round': round,
        'floor': math.floor,
        'ceil': math.ceil,
        'sqrt': math.sqrt,
    }

    # Pattern for $CALCULATE(...)
    CALCULATE_PATTERN = re.compile(r'\$CALCULATE\((.+?)\)')

    def __init__(self):
        self._context: Dict[str, float] = {}

    def set_context(self, context: Dict[str, Any]) -> None:
        """Set variable context for evaluation.

        Args:
            context: Dict with variable values (dimensions, proportions, etc.)
        """
        self._context = {}

        # Flatten context for easy access
        if "dimensions" in context:
            dims = context["dimensions"]
            if isinstance(dims, (list, tuple)) and len(dims) >= 3:
                self._context["width"] = dims[0]
                self._context["height"] = dims[1]
                self._context["depth"] = dims[2]
                self._context["min_dim"] = min(dims)
                self._context["max_dim"] = max(dims)

        if "proportions" in context:
            props = context["proportions"]
            if isinstance(props, dict):
                self._context.update(props)

        # Allow direct values
        for key, value in context.items():
            if isinstance(value, (int, float)):
                self._context[key] = float(value)

    def evaluate(self, expression: str) -> Optional[float]:
        """Evaluate a mathematical expression.

        Args:
            expression: Expression string (without $CALCULATE wrapper)

        Returns:
            Evaluated result or None if invalid.
        """
        try:
            # Tokenize and evaluate
            result = self._safe_eval(expression)
            return result
        except Exception as e:
            logger.warning(f"Expression evaluation failed: {expression} - {e}")
            return None

    def resolve_param_value(
        self,
        value: Any,
    ) -> Any:
        """Resolve a parameter value, evaluating $CALCULATE if present.

        Args:
            value: Parameter value (may contain $CALCULATE)

        Returns:
            Resolved value.
        """
        if not isinstance(value, str):
            return value

        # Check for $CALCULATE(...)
        match = self.CALCULATE_PATTERN.match(value)
        if match:
            expression = match.group(1)
            result = self.evaluate(expression)
            return result if result is not None else value

        # Check for simple $variable reference
        if value.startswith("$") and not value.startswith("$CALCULATE"):
            var_name = value[1:]
            if var_name in self._context:
                return self._context[var_name]

        return value

    def _safe_eval(self, expression: str) -> float:
        """Safely evaluate expression using AST parsing.

        Only allows arithmetic operations and whitelisted functions.
        """
        import ast

        # Replace variable names with values
        for var_name, var_value in self._context.items():
            expression = re.sub(
                rf'\b{var_name}\b',
                str(var_value),
                expression
            )

        # Parse AST
        tree = ast.parse(expression, mode='eval')

        # Validate and evaluate
        return self._eval_node(tree.body)

    def _eval_node(self, node) -> float:
        """Recursively evaluate AST node."""
        import ast

        if isinstance(node, ast.Constant):  # Python 3.8+
            if isinstance(node.value, (int, float)):
                return float(node.value)
            raise ValueError(f"Invalid constant: {node.value}")

        elif isinstance(node, ast.Num):  # Python 3.7 fallback
            return float(node.n)

        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op_type = type(node.op).__name__

            op_map = {
                'Add': operator.add,
                'Sub': operator.sub,
                'Mult': operator.mul,
                'Div': operator.truediv,
                'Pow': operator.pow,
                'Mod': operator.mod,
            }

            if op_type in op_map:
                return op_map[op_type](left, right)
            raise ValueError(f"Unsupported operator: {op_type}")

        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            if isinstance(node.op, ast.USub):
                return -operand
            if isinstance(node.op, ast.UAdd):
                return operand
            raise ValueError(f"Unsupported unary operator")

        elif isinstance(node, ast.Call):
            func_name = node.func.id if isinstance(node.func, ast.Name) else None
            if func_name not in self.FUNCTIONS:
                raise ValueError(f"Function not allowed: {func_name}")
            args = [self._eval_node(arg) for arg in node.args]
            return self.FUNCTIONS[func_name](*args)

        else:
            raise ValueError(f"Unsupported AST node: {type(node)}")
```

**Tests:**
- `tests/unit/router/application/test_expression_evaluator.py`

**Test Cases:**

```python
def test_basic_arithmetic():
    evaluator = ExpressionEvaluator()
    evaluator.set_context({"width": 2.0, "height": 4.0})

    assert evaluator.evaluate("width * 0.5") == 1.0
    assert evaluator.evaluate("height / width") == 2.0
    assert evaluator.evaluate("min(width, height)") == 2.0

def test_calculate_in_param():
    evaluator = ExpressionEvaluator()
    evaluator.set_context({"depth": 0.1})

    result = evaluator.resolve_param_value("$CALCULATE(depth * 0.5)")
    assert result == 0.05
```

**Acceptance Criteria:**
- [x] Basic arithmetic works: `+`, `-`, `*`, `/`, `**`
- [x] Math functions work: `min`, `max`, `abs`, `round`, `sqrt`
- [x] Variable references resolve from context
- [x] Invalid expressions return `None` (not raise)
- [x] No arbitrary code execution possible

---

### TASK-041-8: Integrate Expression Evaluator into WorkflowRegistry ✅

**Priority:** 🟡 Medium (P2)
**Layer:** Application
**Estimated Time:** 1h

**Files to Modify:**

| File | Change |
|------|--------|
| `server/router/application/workflows/registry.py` | Use ExpressionEvaluator in `_resolve_definition_params()` |

**Code Changes:**

```python
# server/router/application/workflows/registry.py

from server.router.application.evaluator.expression_evaluator import ExpressionEvaluator

class WorkflowRegistry:
    def __init__(self):
        # ... existing ...
        self._evaluator = ExpressionEvaluator()

    def expand_workflow(
        self,
        workflow_name: str,
        params: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,  # NEW
    ) -> List[CorrectedToolCall]:
        """Expand workflow with expression evaluation."""

        # Set context for expression evaluation
        if context:
            self._evaluator.set_context(context)
        elif params:
            self._evaluator.set_context(params)

        # ... rest of existing code ...

    def _resolve_definition_params(
        self,
        steps: List[WorkflowStep],
        params: Dict[str, Any],
    ) -> List[WorkflowStep]:
        """Resolve parameter references with expression evaluation."""
        resolved_steps = []

        for step in steps:
            resolved_params = {}
            for key, value in step.params.items():
                # Use evaluator for all value resolution
                resolved_params[key] = self._evaluator.resolve_param_value(value)

                # Fallback: if still starts with $, try direct inheritance
                if isinstance(resolved_params[key], str) and resolved_params[key].startswith("$"):
                    param_name = resolved_params[key][1:]
                    if param_name in params:
                        resolved_params[key] = params[param_name]

            resolved_steps.append(
                WorkflowStep(
                    tool=step.tool,
                    params=resolved_params,
                    description=step.description,
                    condition=step.condition,
                )
            )

        return resolved_steps
```

**Acceptance Criteria:**
- [x] `$CALCULATE(width * 0.1)` evaluates to actual number
- [x] Context from scene (dimensions) is available
- [x] Simple `$param` inheritance still works

---

### TASK-041-9: Pass Scene Context to Workflow Expansion ✅

**Priority:** 🟡 Medium (P2)
**Layer:** Application
**Estimated Time:** 30min

**Files to Modify:**

| File | Change |
|------|--------|
| `server/router/application/router.py` | Pass context to workflow expansion |
| `server/router/application/engines/workflow_expansion_engine.py` | Forward context to registry |

**Code:**

```python
# In SupervisorRouter._expand_triggered_workflow()

def _expand_triggered_workflow(
    self,
    workflow_name: str,
    params: Dict[str, Any],
    context: SceneContext,  # NEW
) -> List[CorrectedToolCall]:
    """Expand workflow with scene context for expressions."""
    registry = get_workflow_registry()

    # Build context dict for expression evaluator
    eval_context = {
        "mode": context.mode,
        **params,
    }

    # Add dimensions if available
    if context.proportions:
        eval_context["proportions"] = context.proportions.__dict__

    active_dims = context.get_active_dimensions()
    if active_dims:
        eval_context["dimensions"] = active_dims
        eval_context["width"] = active_dims[0]
        eval_context["height"] = active_dims[1]
        eval_context["depth"] = active_dims[2]

    return registry.expand_workflow(workflow_name, params, eval_context)
```

---

## Phase 3: Conditional Execution (P3)

### TASK-041-10: Create Condition Evaluator

**Priority:** 🟡 Medium (P3)
**Layer:** Application
**Estimated Time:** 1.5h

**Purpose:** Evaluate `condition` field in workflow steps.

**Files to Create:**

| File | Purpose |
|------|---------|
| `server/router/application/evaluator/condition_evaluator.py` | Boolean condition evaluator |

**Code:**

```python
# server/router/application/evaluator/condition_evaluator.py

import re
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ConditionEvaluator:
    """Evaluates boolean conditions for workflow step execution.

    Supported conditions:
    - "current_mode != 'EDIT'"
    - "has_selection"
    - "not has_selection"
    - "object_count > 0"
    - "active_object == 'Cube'"
    """

    # Comparison operators
    COMPARISONS = {
        '==': lambda a, b: a == b,
        '!=': lambda a, b: a != b,
        '>': lambda a, b: a > b,
        '<': lambda a, b: a < b,
        '>=': lambda a, b: a >= b,
        '<=': lambda a, b: a <= b,
    }

    def __init__(self):
        self._context: Dict[str, Any] = {}

    def set_context(self, context: Dict[str, Any]) -> None:
        """Set evaluation context.

        Expected keys:
        - current_mode: str
        - has_selection: bool
        - object_count: int
        - active_object: str
        - selected_verts: int
        - selected_faces: int
        """
        self._context = context

    def set_context_from_scene(self, scene_context: Any) -> None:
        """Set context from SceneContext object."""
        self._context = {
            "current_mode": scene_context.mode,
            "has_selection": scene_context.has_selection,
            "object_count": len(scene_context.objects) if scene_context.objects else 0,
            "active_object": scene_context.active_object,
        }

        if scene_context.topology:
            self._context["selected_verts"] = scene_context.topology.selected_verts
            self._context["selected_edges"] = scene_context.topology.selected_edges
            self._context["selected_faces"] = scene_context.topology.selected_faces

    def evaluate(self, condition: str) -> bool:
        """Evaluate a condition string.

        Args:
            condition: Condition expression.

        Returns:
            True if condition is met, False otherwise.
            Returns True if condition is invalid (fail-open).
        """
        if not condition or not condition.strip():
            return True

        condition = condition.strip()

        try:
            # Handle "not X" prefix
            if condition.startswith("not "):
                inner = condition[4:].strip()
                return not self.evaluate(inner)

            # Handle boolean variables directly
            if condition in self._context:
                return bool(self._context[condition])

            # Handle comparisons
            for op, func in self.COMPARISONS.items():
                if op in condition:
                    parts = condition.split(op, 1)
                    if len(parts) == 2:
                        left = self._resolve_value(parts[0].strip())
                        right = self._resolve_value(parts[1].strip())
                        return func(left, right)

            logger.warning(f"Could not parse condition: {condition}")
            return True  # Fail-open

        except Exception as e:
            logger.error(f"Condition evaluation failed: {condition} - {e}")
            return True  # Fail-open

    def _resolve_value(self, value_str: str) -> Any:
        """Resolve a value from string representation."""
        value_str = value_str.strip()

        # String literal
        if (value_str.startswith("'") and value_str.endswith("'")) or \
           (value_str.startswith('"') and value_str.endswith('"')):
            return value_str[1:-1]

        # Number
        try:
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            pass

        # Boolean
        if value_str.lower() == 'true':
            return True
        if value_str.lower() == 'false':
            return False

        # Variable reference
        if value_str in self._context:
            return self._context[value_str]

        return value_str
```

**Tests:**
- `tests/unit/router/application/test_condition_evaluator.py`

**Test Cases:**

```python
def test_mode_condition():
    evaluator = ConditionEvaluator()
    evaluator.set_context({"current_mode": "OBJECT"})

    assert evaluator.evaluate("current_mode != 'EDIT'") == True
    assert evaluator.evaluate("current_mode == 'OBJECT'") == True
    assert evaluator.evaluate("current_mode == 'EDIT'") == False

def test_boolean_condition():
    evaluator = ConditionEvaluator()
    evaluator.set_context({"has_selection": True})

    assert evaluator.evaluate("has_selection") == True
    assert evaluator.evaluate("not has_selection") == False
```

---

### TASK-041-11: Integrate Condition Evaluator into Workflow Execution

**Priority:** 🟡 Medium (P3)
**Layer:** Application
**Estimated Time:** 1h

**Files to Modify:**

| File | Change |
|------|--------|
| `server/router/application/workflows/registry.py` | Skip steps where condition is False |

**Code Changes:**

```python
# server/router/application/workflows/registry.py

from server.router.application.evaluator.condition_evaluator import ConditionEvaluator

class WorkflowRegistry:
    def __init__(self):
        # ... existing ...
        self._condition_evaluator = ConditionEvaluator()

    def expand_workflow(
        self,
        workflow_name: str,
        params: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[CorrectedToolCall]:
        # ... get steps as before ...

        # Set condition context
        if context:
            self._condition_evaluator.set_context(context)

        # Filter steps by condition
        calls = []
        for i, step in enumerate(steps):
            # Check condition
            if step.condition:
                should_execute = self._condition_evaluator.evaluate(step.condition)
                if not should_execute:
                    logger.debug(f"Skipping step {i+1} ({step.tool}): condition not met")
                    continue

            call = CorrectedToolCall(
                tool_name=step.tool,
                params=dict(step.params),
                corrections_applied=[f"workflow:{workflow_name}:step_{i+1}"],
                is_injected=True,
            )
            calls.append(call)

        return calls
```

**YAML Example:**

```yaml
steps:
  - tool: system_set_mode
    params: { mode: "EDIT" }
    condition: "current_mode != 'EDIT'"  # Only switch if not already in EDIT

  - tool: mesh_select
    params: { action: "all" }
    condition: "not has_selection"  # Only select if nothing selected
```

**Acceptance Criteria:**
- [ ] Steps with false conditions are skipped
- [ ] Empty/missing condition means always execute
- [ ] Logging shows which steps were skipped

---

### TASK-041-12: Update Context During Workflow Execution

**Priority:** 🟡 Medium (P3)
**Layer:** Application
**Estimated Time:** 1h

**Problem:** Conditions need updated context as workflow progresses (e.g., mode changes).

**Files to Modify:**

| File | Change |
|------|--------|
| `server/router/application/workflows/registry.py` | Simulate context changes |

**Code:**

```python
# server/router/application/workflows/registry.py

class WorkflowRegistry:
    def expand_workflow(
        self,
        workflow_name: str,
        params: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[CorrectedToolCall]:
        # ... existing setup ...

        # Track simulated context for conditions
        simulated_context = dict(context) if context else {}

        calls = []
        for i, step in enumerate(steps):
            # Check condition with current simulated context
            if step.condition:
                self._condition_evaluator.set_context(simulated_context)
                should_execute = self._condition_evaluator.evaluate(step.condition)
                if not should_execute:
                    continue

            # ... create call ...
            calls.append(call)

            # Update simulated context based on step
            self._update_simulated_context(simulated_context, step)

        return calls

    def _update_simulated_context(
        self,
        context: Dict[str, Any],
        step: WorkflowStep,
    ) -> None:
        """Update simulated context after step would execute."""

        if step.tool == "system_set_mode":
            context["current_mode"] = step.params.get("mode", context.get("current_mode"))

        elif step.tool == "mesh_select":
            action = step.params.get("action")
            if action == "all":
                context["has_selection"] = True
            elif action == "none":
                context["has_selection"] = False
```

---

## Phase 4: Scene-Relative Parameters (P4)

### TASK-041-13: Create ProportionResolver

**Priority:** 🟢 Low (P4)
**Layer:** Application
**Estimated Time:** 1h

**Purpose:** Auto-calculate params relative to object dimensions.

**Files to Create:**

| File | Purpose |
|------|---------|
| `server/router/application/evaluator/proportion_resolver.py` | Dimension-relative param resolution |

**Code:**

```python
# server/router/application/evaluator/proportion_resolver.py

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class ProportionResolver:
    """Resolves parameters relative to object proportions.

    Supports:
    - $AUTO_BEVEL: 5% of smallest dimension
    - $AUTO_INSET: 3% of face area
    - $AUTO_EXTRUDE: 10% of height

    These are "smart defaults" when exact values aren't provided.
    """

    # Auto-param definitions
    AUTO_PARAMS = {
        "$AUTO_BEVEL": {
            "calculation": lambda dims: min(dims) * 0.05,
            "description": "5% of smallest dimension",
        },
        "$AUTO_INSET": {
            "calculation": lambda dims: min(dims[0], dims[1]) * 0.03,
            "description": "3% of XY plane smallest dimension",
        },
        "$AUTO_EXTRUDE": {
            "calculation": lambda dims: dims[2] * 0.1,
            "description": "10% of Z height",
        },
        "$AUTO_SCALE_SMALL": {
            "calculation": lambda dims: [d * 0.8 for d in dims],
            "description": "80% of current size",
        },
    }

    def __init__(self):
        self._dimensions: Optional[List[float]] = None

    def set_dimensions(self, dimensions: List[float]) -> None:
        """Set object dimensions for calculations."""
        self._dimensions = dimensions

    def resolve(self, value: Any) -> Any:
        """Resolve a parameter value.

        Args:
            value: Parameter value (may be $AUTO_* reference).

        Returns:
            Resolved value.
        """
        if not isinstance(value, str) or not value.startswith("$AUTO_"):
            return value

        if self._dimensions is None:
            logger.warning(f"Cannot resolve {value}: no dimensions set")
            return value

        if value in self.AUTO_PARAMS:
            calc = self.AUTO_PARAMS[value]["calculation"]
            result = calc(self._dimensions)
            logger.debug(f"Resolved {value} -> {result}")
            return result

        return value
```

**YAML Example:**

```yaml
steps:
  - tool: mesh_bevel
    params:
      width: "$AUTO_BEVEL"  # Resolves to min(dims) * 0.05
      segments: 3
```

---

### TASK-041-14: Integrate ProportionResolver

**Priority:** 🟢 Low (P4)
**Layer:** Application
**Estimated Time:** 30min

**Files to Modify:**

| File | Change |
|------|--------|
| `server/router/application/workflows/registry.py` | Add proportion resolution |

---

## Phase 5: Testing & Documentation

### TASK-041-15: E2E Tests for YAML Workflows

**Priority:** 🟡 Medium
**Layer:** Testing
**Estimated Time:** 2h

**Files to Create:**

| File | Purpose |
|------|---------|
| `tests/e2e/router/test_yaml_workflow_execution.py` | End-to-end workflow tests |
| `tests/e2e/router/test_workflow_triggering.py` | Trigger mechanism tests |
| `server/router/application/workflows/custom/test_workflow.yaml` | Test workflow |

**Test Scenarios:**

1. **YAML workflow loads and executes**
2. **Keyword trigger activates workflow**
3. **$CALCULATE expressions evaluate correctly**
4. **Conditions skip appropriate steps**
5. **$AUTO_* params resolve to correct values**

---

### TASK-041-16: Documentation Update

**Priority:** 🟡 Medium
**Layer:** Documentation
**Estimated Time:** 1h

**Files to Create/Update:**

| File | Change |
|------|--------|
| `_docs/_ROUTER/WORKFLOWS/yaml-workflow-guide.md` | Complete YAML workflow guide |
| `_docs/_ROUTER/WORKFLOWS/expression-reference.md` | Expression syntax reference |
| `_docs/_ROUTER/README.md` | Add YAML workflow section |
| `_docs/_CHANGELOG/82-YYYY-MM-DD-yaml-workflow-integration.md` | Changelog |

---

## Summary

| Phase | Tasks | Priority | Estimated Time |
|-------|-------|----------|----------------|
| **Phase -1: Intent Source** | 2 tasks | 🔴 Critical | 2h |
| **P0: Connect YAML** | 3 tasks | 🔴 High | 2.5h |
| **P1: Auto-Trigger** | 3 tasks | 🔴 High | 3.5h |
| **P2: Expressions** | 3 tasks | 🟡 Medium | 3.5h |
| **P3: Conditions** | 3 tasks | 🟡 Medium | 3.5h |
| **P4: Proportions** | 2 tasks | 🟢 Low | 1.5h |
| **Testing/Docs** | 2 tasks | 🟡 Medium | 3h |
| **TOTAL** | **18 tasks** | | **~19.5h** |

---

## Dependencies

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE -1 (PREREQUISITE)                                        │
│                                                                 │
│  TASK-041-0 (router_set_goal tool)                              │
│       │                                                         │
│       └──▶ TASK-041-0b (heuristics fallback)                    │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
TASK-041-1 ──┬──▶ TASK-041-2 ──▶ TASK-041-3
             │
             └──▶ TASK-041-4 ──▶ TASK-041-5 ──▶ TASK-041-6

TASK-041-7 ──▶ TASK-041-8 ──▶ TASK-041-9

TASK-041-10 ──▶ TASK-041-11 ──▶ TASK-041-12

TASK-041-13 ──▶ TASK-041-14

All ──▶ TASK-041-15 ──▶ TASK-041-16
```

---

## Quick Start After Implementation

```yaml
# workflows/custom/house_simple.yaml
name: house_simple
description: Simple house with roof
trigger_keywords: ["house", "building", "home", "cottage"]

steps:
  - tool: modeling_create_primitive
    params: { type: "CUBE" }
    description: "Create base"

  - tool: modeling_transform_object
    params:
      scale: [4, 3, 2.5]
    description: "Scale to house proportions"

  - tool: system_set_mode
    params: { mode: "EDIT" }
    condition: "current_mode != 'EDIT'"

  - tool: mesh_select
    params: { action: "all" }
    condition: "not has_selection"

  - tool: mesh_bevel
    params:
      width: "$CALCULATE(min_dim * 0.02)"
      segments: 2
```

```bash
# Test it works
ROUTER_ENABLED=true docker run -i --rm blender-mcp-server

# In Claude: "create a house"
# → Router triggers house_simple workflow automatically
```
