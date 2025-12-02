# 24. WorkflowTriggerer Integration (TASK-041 P1)

**Task:** TASK-041-4, TASK-041-5, TASK-041-6
**Date:** 2025-12-02
**Status:** Completed

---

## Overview

Integrated WorkflowTriggerer into SupervisorRouter pipeline. Workflows can now be triggered automatically based on:
1. Goal set via `router_set_goal` (priority 1)
2. Heuristics from WorkflowTriggerer (priority 2)

---

## Pipeline Update

Updated SupervisorRouter pipeline from 8 to 10 steps:

```
Before:
1. Intercept → 2. Analyze → 3. Detect → 4. Correct →
5. Override → 6. Expand → 7. Firewall → 8. Execute

After:
1. Intercept → 2. Analyze → 3. Detect → 4. Correct →
5. Trigger → 6. Override → 7. Expand → 8. Build →
9. Firewall → 10. Execute
```

---

## New Components

### WorkflowTriggerer in SupervisorRouter

```python
# server/router/application/router.py

from server.router.application.triggerer.workflow_triggerer import WorkflowTriggerer

class SupervisorRouter:
    def __init__(self, ...):
        # ... existing components ...
        self.triggerer = WorkflowTriggerer()
```

---

## New Methods

### _check_workflow_trigger()

```python
def _check_workflow_trigger(
    self,
    tool_name: str,
    params: Dict[str, Any],
    context: SceneContext,
    pattern: Optional[DetectedPattern],
) -> Optional[str]:
    """Check if a workflow should be triggered.

    Priority:
    1. Pending workflow from goal (set via router_set_goal)
    2. WorkflowTriggerer heuristics
    """
    if not self.config.enable_workflow_expansion:
        return None

    # Priority 1: Use pending workflow from goal
    if self._pending_workflow:
        self.logger.log_info(
            f"Using pending workflow from goal: {self._pending_workflow}"
        )
        return self._pending_workflow

    # Priority 2: Check triggerer heuristics
    workflow_name = self.triggerer.determine_workflow(
        tool_name, params, context, pattern
    )

    if workflow_name:
        self.logger.log_info(
            f"Workflow triggered by heuristics: {workflow_name}"
        )

    return workflow_name
```

### _expand_triggered_workflow()

```python
def _expand_triggered_workflow(
    self,
    workflow_name: str,
    params: Dict[str, Any],
    context: SceneContext,
) -> Optional[List[CorrectedToolCall]]:
    """Expand a triggered workflow by name."""
    registry = get_workflow_registry()
    registry.ensure_custom_loaded()

    # Expand workflow
    calls = registry.expand_workflow(workflow_name, params)

    if calls:
        self._processing_stats["workflows_expanded"] += 1
        self.logger.log_info(
            f"Expanded workflow '{workflow_name}' to {len(calls)} steps"
        )
        # Clear pending workflow after expansion
        self._pending_workflow = None

    return calls
```

---

## Updated process_llm_tool_call()

```python
def process_llm_tool_call(self, tool_name, params, prompt=None):
    # Steps 1-4: Intercept, Analyze, Detect, Correct (unchanged)

    # Step 5: Check workflow trigger (NEW!)
    triggered_workflow = self._check_workflow_trigger(
        tool_name, params, context, pattern
    )

    # Step 6: Override - skip if workflow triggered
    override_result = None
    if not triggered_workflow:
        override_result = self._check_override(tool_name, params, context, pattern)

    # Step 7: Expand - use triggered workflow or default expansion
    expanded = None
    if triggered_workflow:
        expanded = self._expand_triggered_workflow(triggered_workflow, params, context)
    elif not override_result:
        expanded = self._expand_workflow(tool_name, params, context, pattern)

    # Steps 8-10: Build, Firewall, Execute (unchanged)
```

---

## Trigger Priority Flow

```
┌─────────────────────────────────────────────────────────┐
│                   _check_workflow_trigger()              │
└────────────────────────┬────────────────────────────────┘
                         │
          ┌──────────────▼──────────────┐
          │ Is _pending_workflow set?   │
          │ (from router_set_goal)      │
          └──────────────┬──────────────┘
                         │
        ┌────────────────┴────────────────┐
        │ YES                             │ NO
        ▼                                 ▼
┌───────────────────┐      ┌─────────────────────────────┐
│ Return pending    │      │ Check triggerer.determine_  │
│ workflow          │      │ workflow() for heuristics   │
└───────────────────┘      └──────────────┬──────────────┘
                                          │
                           ┌──────────────▼──────────────┐
                           │ Flat/tall shape detected?   │
                           └──────────────┬──────────────┘
                                          │
                          ┌───────────────┴───────────────┐
                          │ YES                           │ NO
                          ▼                               ▼
                   ┌─────────────┐               ┌─────────────┐
                   │ Return      │               │ Return None │
                   │ workflow    │               │ (no trigger)│
                   └─────────────┘               └─────────────┘
```

---

## Tests

All 561 router tests pass after integration.

---

## See Also

- [23-yaml-workflow-integration.md](./23-yaml-workflow-integration.md) - Phase -1, P0
- [WorkflowTriggerer](../../../server/router/application/triggerer/workflow_triggerer.py)
- [SupervisorRouter](../../../server/router/application/router.py)
