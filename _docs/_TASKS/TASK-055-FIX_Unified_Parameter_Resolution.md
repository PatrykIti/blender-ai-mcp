# TASK-055-FIX: Unified Interactive Parameter Resolution

## Status: ✅ Done
## Priority: 🔴 High
## Created: 2025-12-08
## Completed: 2025-12-11

---

## Overview

**Fix TASK-055 implementation** to use a single unified `router_set_goal` tool instead of 4 separate tools. The LLM should interact with the Router through one tool only, with automatic parameter resolution and workflow execution.

## Problem Statement

TASK-055 was implemented with **4 separate MCP tools**:
- `router_set_goal_interactive` - sets goal with parameter details
- `router_store_parameter` - stores resolved parameter value
- `router_list_parameters` - lists stored mappings
- `router_delete_parameter` - deletes stored mapping

This breaks context and forces the LLM to juggle multiple tools. The user specified that:

> "przez tego toola jednego miala przechodzic konwersacja.. bo inaczej bedziemy tracili kontekst"

(The conversation should go through one tool, otherwise we lose context)

## Solution

**Single tool `router_set_goal`** handles everything:

```python
@mcp.tool()
def router_set_goal(
    ctx: Context,
    goal: str,
    resolved_params: Optional[Dict[str, Any]] = None
) -> str:
    """Sets goal, resolves parameters, and executes workflow."""
```

### Flow 1: All Parameters Resolved (Happy Path)

```
User: router_set_goal("prosty stół z 4 prostymi nogami")
       ↓
Router:
  1. Matches picnic_table_workflow
  2. Resolves parameters (from YAML modifiers OR learned LanceDB)
  3. Executes workflow with resolved values
       ↓
Returns: {
    "status": "ready",
    "workflow": "picnic_table_workflow",
    "resolved": {"leg_angle_left": 0, "leg_angle_right": 0},
    "message": "Workflow executed successfully"
}
```

### Flow 2: Unresolved Parameters (Interactive)

```
User: router_set_goal("stół z nogami pod kątem")
       ↓
Router:
  1. Matches picnic_table_workflow
  2. Cannot resolve leg_angle_left (not in YAML, not learned)
  3. Returns question to LLM
       ↓
Returns: {
    "status": "needs_input",
    "workflow": "picnic_table_workflow",
    "unresolved": [{
        "param": "leg_angle_left",
        "description": "Kąt lewych nóg (0=proste)",
        "range": [0, 45],
        "default": 0.32
    }]
}
       ↓
User: router_set_goal("stół z nogami pod kątem", resolved_params={"leg_angle_left": 15})
       ↓
Router:
  1. Stores mapping "nogami pod kątem" → leg_angle_left=15 (LanceDB)
  2. Executes workflow with leg_angle_left=15
       ↓
Returns: {
    "status": "ready",
    "workflow": "picnic_table_workflow",
    "resolved": {"leg_angle_left": 15, ...},
    "message": "Workflow executed successfully"
}
```

### Flow 3: Future Semantic Matching

```
User: router_set_goal("stół z pochylonymi nogami")
       ↓
Router:
  1. Matches picnic_table_workflow
  2. LaBSE finds similarity: "pochylonymi nogami" ≈ "nogami pod kątem" (0.87)
  3. Uses stored value: leg_angle_left=15
  4. Executes workflow
       ↓
Returns: {
    "status": "ready",
    "resolved": {"leg_angle_left": 15, ...},
    "resolution_sources": {"leg_angle_left": "learned"}
}
```

---

## Sub-tasks

### TASK-055-FIX-1: Modify router_set_goal Tool
**Status:** ✅ Done

Update MCP tool signature and logic:

**File:** `server/adapters/mcp/areas/router.py`

```python
@mcp.tool()
def router_set_goal(
    ctx: Context,
    goal: str,
    resolved_params: Optional[Dict[str, Any]] = None
) -> str:
    """[SYSTEM][CRITICAL] Sets modeling goal with automatic parameter resolution.

    This is the ONLY tool needed for workflow interaction:
    1. First call: Set goal, Router matches workflow
    2. If unresolved params: Returns questions for LLM
    3. Second call: Provide resolved_params, Router executes workflow

    Learned mappings are stored automatically for future semantic reuse.

    Args:
        goal: What you're building (e.g., "smartphone", "table with angled legs")
        resolved_params: Optional dict of parameter values when answering Router questions

    Returns:
        JSON with:
        - status: "ready" | "needs_input" | "no_match"
        - workflow: matched workflow name
        - resolved: dict of resolved parameter values
        - unresolved: list of parameters needing LLM input (when status="needs_input")
        - message: execution result or next steps

    Example:
        # Step 1: Set goal
        router_set_goal("stół z prostymi nogami")
        → {"status": "ready", "workflow": "picnic_table", ...}

        # Or if unresolved:
        router_set_goal("stół z nogami pod kątem")
        → {"status": "needs_input", "unresolved": [...]}

        # Step 2: Provide values
        router_set_goal("stół z nogami pod kątem", resolved_params={"leg_angle": 15})
        → {"status": "ready", ...}
    """
```

**Changes:**
- Add `resolved_params: Optional[Dict[str, Any]] = None` argument
- Remove separate tools: `router_set_goal_interactive`, `router_store_parameter`, `router_list_parameters`, `router_delete_parameter`

---

### TASK-055-FIX-2: Modify RouterToolHandler.set_goal()
**Status:** ✅ Done

Merge interactive logic into main `set_goal()` method:

**File:** `server/application/tool_handlers/router_handler.py`

```python
def set_goal(
    self,
    goal: str,
    resolved_params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Set goal with automatic parameter resolution and workflow execution.

    Args:
        goal: User's modeling goal
        resolved_params: Optional LLM-provided parameter values

    Returns:
        Dict with status, workflow, resolved params, unresolved params
    """
    # 1. Match workflow
    matched_workflow = router.set_current_goal(goal)
    if not matched_workflow:
        return {"status": "no_match", "message": f"No workflow matched for: {goal}"}

    # 2. Get workflow definition and parameters
    workflow = loader.get_workflow(matched_workflow)

    # 3. If resolved_params provided, store them first
    if resolved_params:
        for param_name, value in resolved_params.items():
            context = self._extract_context_for_param(goal, param_name)
            self._parameter_store.store_mapping(
                context=context,
                parameter_name=param_name,
                value=value,
                workflow_name=matched_workflow
            )

    # 4. Resolve all parameters (3-tier system)
    resolution = self._parameter_resolver.resolve(
        prompt=goal,
        workflow_name=matched_workflow,
        parameters=workflow.parameters,
        existing_modifiers=router._pending_modifiers or {}
    )

    # 5. Check if we need more input
    if resolution.needs_llm_input:
        return {
            "status": "needs_input",
            "workflow": matched_workflow,
            "resolved": resolution.resolved,
            "unresolved": [
                {
                    "param": p.name,
                    "description": p.schema.description,
                    "range": list(p.schema.range) if p.schema.range else None,
                    "default": p.schema.default,
                    "context": p.context
                }
                for p in resolution.unresolved
            ],
            "resolution_sources": resolution.resolution_sources
        }

    # 6. All resolved - execute workflow
    # Store resolved params as pending variables for workflow execution
    router._pending_variables = resolution.resolved

    return {
        "status": "ready",
        "workflow": matched_workflow,
        "resolved": resolution.resolved,
        "resolution_sources": resolution.resolution_sources,
        "message": f"Workflow '{matched_workflow}' ready to execute with {len(resolution.resolved)} parameters"
    }
```

**Methods to DELETE:**
- `store_parameter_value()`
- `list_parameter_mappings()`
- `delete_parameter_mapping()`
- `set_goal_interactive()`
- `set_goal_interactive_formatted()`

---

### TASK-055-FIX-3: Simplify IParameterStore Interface
**Status:** ✅ Done

Remove unused methods from interface:

**File:** `server/router/domain/interfaces/i_parameter_resolver.py`

```python
class IParameterStore(ABC):
    """Abstract interface for parameter mapping storage."""

    @abstractmethod
    def find_mapping(
        self,
        prompt: str,
        parameter_name: str,
        workflow_name: str,
        similarity_threshold: float = 0.85
    ) -> Optional[StoredMapping]:
        """Find semantically similar stored mapping."""
        pass

    @abstractmethod
    def store_mapping(
        self,
        context: str,
        parameter_name: str,
        value: Any,
        workflow_name: str
    ) -> None:
        """Store LLM-provided value with embedding."""
        pass

    @abstractmethod
    def increment_usage(self, mapping: StoredMapping) -> None:
        """Increment usage count for analytics."""
        pass

    # REMOVED: list_mappings() - not needed
    # REMOVED: delete_mapping() - not needed
    # REMOVED: get_stats() - not needed
```

---

### TASK-055-FIX-4: Simplify ParameterStore Implementation
**Status:** ✅ Done

Remove unused methods from implementation:

**File:** `server/router/application/resolver/parameter_store.py`

**Methods to DELETE:**
- `list_mappings()`
- `delete_mapping()`
- `get_stats()`

**Methods to KEEP:**
- `find_mapping()`
- `store_mapping()`
- `increment_usage()`
- `clear()` - for testing

---

### TASK-055-FIX-5: Update Tests
**Status:** ✅ Done

Update tests to reflect new unified interface:

**Files to modify:**
- `tests/unit/router/application/resolver/test_parameter_store.py` - remove tests for deleted methods
- `tests/unit/router/application/resolver/test_parameter_resolver.py` - keep as-is
- `tests/unit/application/test_router_handler_parameters.py` - update for new set_goal signature
- `tests/e2e/router/test_parameter_resolution.py` - update for unified flow

**New test scenarios:**
```python
def test_set_goal_with_resolved_params():
    """Test providing resolved_params on second call."""
    handler = RouterToolHandler()

    # First call - returns needs_input
    result1 = handler.set_goal("stół z nogami pod kątem")
    assert result1["status"] == "needs_input"

    # Second call - with resolved_params
    result2 = handler.set_goal(
        "stół z nogami pod kątem",
        resolved_params={"leg_angle_left": 15}
    )
    assert result2["status"] == "ready"
    assert result2["resolved"]["leg_angle_left"] == 15

def test_stored_mapping_auto_resolves():
    """Test that stored mapping is reused via LaBSE."""
    handler = RouterToolHandler()

    # First: provide value
    handler.set_goal("stół z pochylonymi nogami", resolved_params={"leg_angle": 15})

    # Second: similar prompt auto-resolves
    result = handler.set_goal("stół z skośnymi nogami")  # Similar meaning
    assert result["status"] == "ready"
    assert result["resolution_sources"]["leg_angle"] == "learned"
```

---

### TASK-055-FIX-6: Update Documentation
**Status:** ✅ Done

Update documentation to reflect unified tool:

**Files to update:**
- `_docs/_MCP_SERVER/README.md` - remove 4 tools, update router_set_goal
- `_docs/AVAILABLE_TOOLS_SUMMARY.md` - same
- `_docs/_ROUTER/README.md` - update TASK-055 section
- `_docs/_CHANGELOG/100-2025-12-08-interactive-parameter-resolution.md` - update

**New router_set_goal documentation:**
```markdown
| Tool | Arguments | Description |
|------|-----------|-------------|
| `router_set_goal` | `goal` (str), `resolved_params` (dict, optional) | Sets modeling goal with automatic parameter resolution. When unresolved params exist, returns questions. Call again with resolved_params to provide answers. |
```

---

## Implementation Order

1. **TASK-055-FIX-1** - Modify MCP tool signature
2. **TASK-055-FIX-2** - Merge handler logic
3. **TASK-055-FIX-3** - Simplify interface
4. **TASK-055-FIX-4** - Simplify implementation
5. **TASK-055-FIX-5** - Update tests
6. **TASK-055-FIX-6** - Update documentation
7. Rebuild Docker image

## Files to Modify

| File | Action |
|------|--------|
| `server/adapters/mcp/areas/router.py` | Remove 4 tools, modify router_set_goal |
| `server/application/tool_handlers/router_handler.py` | Remove 5 methods, modify set_goal |
| `server/router/domain/interfaces/i_parameter_resolver.py` | Remove list_mappings, delete_mapping |
| `server/router/application/resolver/parameter_store.py` | Remove list_mappings, delete_mapping, get_stats |
| `tests/unit/router/application/resolver/test_parameter_store.py` | Remove tests for deleted methods |
| `tests/unit/application/test_router_handler_parameters.py` | Update for new set_goal |
| `tests/e2e/router/test_parameter_resolution.py` | Update for unified flow |
| `_docs/_MCP_SERVER/README.md` | Update tool list |
| `_docs/AVAILABLE_TOOLS_SUMMARY.md` | Update tool list |
| `_docs/_ROUTER/README.md` | Update TASK-055 section |
| `_docs/_CHANGELOG/100-*.md` | Update changelog |

## Key Design Decisions

1. **Single tool for entire conversation** - No context loss between calls
2. **resolved_params argument** - LLM provides values through same tool
3. **Auto-store on resolve** - When resolved_params provided, mapping is stored automatically
4. **No list/delete tools** - Mappings manage themselves, no manual management needed
5. **Execute on ready** - When all params resolved, workflow executes automatically

## Estimated Effort

- Sub-tasks: 6
- Estimated LOC: -200 (removing more than adding)
- Complexity: Low (mostly deletion and simplification)
