# Changelog 84: WorkflowTriggerer Integration (TASK-041 P1)

**Date:** 2025-12-02
**Task:** [TASK-041](../_TASKS/TASK-041_Router_YAML_Workflow_Integration.md)
**Type:** Feature

---

## Summary

Integrated WorkflowTriggerer into SupervisorRouter pipeline. Now workflows can be triggered automatically based on goal (from `router_set_goal`) or heuristics.

---

## Changes

### SupervisorRouter Pipeline Update

Updated pipeline from 8 to 10 steps:

```
1. Intercept → capture LLM tool call
2. Analyze → read scene context
3. Detect → identify geometry patterns
4. Correct → fix params/mode/selection
5. Trigger → check for workflow trigger (NEW!)
6. Override → check for better alternatives
7. Expand → transform to workflow
8. Build → build final tool sequence
9. Firewall → validate each tool
10. Execute → return final tool list
```

### New Components

| Component | Purpose |
|-----------|---------|
| `WorkflowTriggerer` | Added as `self.triggerer` in SupervisorRouter |

### New Methods

| Method | Purpose |
|--------|---------|
| `_check_workflow_trigger()` | Check for workflow trigger (goal or heuristics) |
| `_expand_triggered_workflow()` | Expand triggered workflow by name |

### Trigger Priority

1. **Pending workflow from goal** - set via `router_set_goal` MCP tool
2. **WorkflowTriggerer heuristics** - flat/tall shape detection

---

## File Modified

| File | Change |
|------|--------|
| `server/router/application/router.py` | Added WorkflowTriggerer, new pipeline step 5, new methods |

---

## Logic Flow

```python
# In process_llm_tool_call:

# Step 5: Check workflow trigger
triggered_workflow = self._check_workflow_trigger(
    tool_name, params, context, pattern
)

# Step 6: Override - skip if workflow triggered
if not triggered_workflow:
    override_result = self._check_override(...)

# Step 7: Expand
if triggered_workflow:
    expanded = self._expand_triggered_workflow(triggered_workflow, params, context)
elif not override_result:
    expanded = self._expand_workflow(...)
```

---

## Tests

All 561 router tests pass.
