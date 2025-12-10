# TASK-055-FIX-4: Router Workflow Parameter Passing Bug

**Status**: 🚧 In Progress
**Priority**: Critical
**Category**: Bug Fix
**Blocking**: Conditional workflow steps for X-shaped legs

---

## Problem

Conditional workflow steps don't execute for X-shaped legs when using `router_set_goal` tool, despite parameters being correctly resolved.

### Symptoms

**Test Case 1 - Picnic Table Default** (leg_angle: 0.32/-0.32):
- ✅ Expected: 47 tool calls (conditional steps skipped)
- ✅ Actual: 47 tool calls
- ✅ Behavior: Correct

**Test Case 2 - Straight Legs** (leg_angle: 0/0):
- ✅ Expected: 22 tool calls (conditional steps skipped)
- ✅ Actual: 22 tool calls
- ✅ Behavior: Correct

**Test Case 3 - X-Shaped Legs** (leg_angle: 1.0/-1.0):
- ✅ Expected: 67 tool calls (conditional steps EXECUTE)
- ❌ Actual: 22 tool calls (conditional steps SKIPPED)
- ❌ Behavior: WRONG - legs too short, not stretched to table top

### Root Cause Analysis

**Poetry Python Test** (`debug_condition_flow.py`):
- Direct workflow expansion works correctly: 67 tool calls ✅
- Direct condition evaluation works: `leg_angle_left > 0.5` → True ✅
- **Conclusion**: Core code (WorkflowRegistry, ConditionEvaluator) is correct

**Blender Test** (`router_set_goal`):
- Parameters resolved correctly: `leg_angle_left: 1.0, leg_angle_right: -1.0` ✅
- Workflow executed: 22 tool calls ❌ (should be 67)
- **Conclusion**: Bug is in RouterToolHandler → SupervisorRouter → execute_pending_workflow

### Bugs Found

**File**: `server/router/application/router.py`

**Bug 1 - Line 1397**: Missing `final_variables` in condition context

```python
# BEFORE (BUG):
registry._condition_evaluator.set_context(registry._build_condition_context(eval_context))

# AFTER (FIX):
extended_context = {**registry._build_condition_context(eval_context), **final_variables}
registry._condition_evaluator.set_context(extended_context)
```

**Problem**: Condition evaluator receives only `eval_context` (scene data: mode, dimensions, etc.) but NOT `final_variables` which contains the resolved workflow parameters like `leg_angle_left: 1.0`.

**Bug 2 - Line 1400**: Missing `workflow_params` argument

```python
# BEFORE (BUG):
calls = registry._steps_to_calls(resolved_steps, workflow_name)

# AFTER (FIX):
calls = registry._steps_to_calls(resolved_steps, workflow_name, workflow_params=final_variables)
```

**Problem**: The `_steps_to_calls()` method expects a third argument `workflow_params` which it uses to extend the condition context (registry.py lines 398-403). Without this argument, the workflow parameters never reach the condition evaluator.

**Correct Usage** (for comparison, registry.py line 254):
```python
return self._steps_to_calls(steps, workflow_name, workflow_params=all_params)
```

### Why This Causes the Bug

1. Condition evaluator has context with scene data but NO workflow parameters
2. Condition: `leg_angle_left > 0.5`
3. Variable `leg_angle_left` not in context
4. ConditionEvaluator._resolve_value() returns `0` (TASK-055-FIX-3)
5. Comparison: `0 > 0.5` → False
6. Conditional steps skipped ❌

---

## Solution

Apply two-line fix to `server/router/application/router.py` in the `execute_pending_workflow()` method:

### Fix 1: Line 1397

```python
# Add final_variables to condition context
extended_context = {**registry._build_condition_context(eval_context), **final_variables}
registry._condition_evaluator.set_context(extended_context)
```

### Fix 2: Line 1400

```python
# Pass workflow_params to _steps_to_calls
calls = registry._steps_to_calls(resolved_steps, workflow_name, workflow_params=final_variables)
```

---

## Implementation Plan

### Step 1: Apply Code Fixes

1. Edit `server/router/application/router.py` line 1397
2. Edit `server/router/application/router.py` line 1400

### Step 2: Rebuild Docker

```bash
docker build -t blender-ai-mcp:latest .
```

### Step 3: Restart Container

```bash
docker stop c05b6eea436e
docker rm c05b6eea436e
docker run -d \
  --name blender-mcp \
  -p 3000:3000 \
  -v /tmp/blender_socket:/tmp/blender_socket \
  blender-ai-mcp:latest
```

### Step 4: Test in Blender

**Test 1 - X-shaped legs**:
```python
mcp__blender-mcp-server__router_set_goal(goal="stół z nogami w X")
```
- Expected: 67 tool calls
- Expected: Legs stretched to reach table top

**Test 2 - Picnic table**:
```python
mcp__blender-mcp-server__router_set_goal(goal="stół piknikowy")
```
- Expected: 47 tool calls
- Expected: Legs NOT stretched (angled but correct length)

**Test 3 - Straight legs**:
```python
mcp__blender-mcp-server__router_set_goal(goal="stół z prostymi nogami")
```
- Expected: 22 tool calls
- Expected: Legs NOT stretched (vertical and correct length)

---

## Success Criteria

- ✅ X-shaped legs: 67 tool calls (conditional steps execute)
- ✅ Picnic table: 47 tool calls (conditional steps skipped)
- ✅ Straight legs: 22 tool calls (conditional steps skipped)
- ✅ Geometry correct for all 3 variants
- ✅ No regression in other workflows

---

## Files Modified

1. `server/router/application/router.py` (lines 1397, 1400)

---

## Related Tasks

- **TASK-055**: Router Interactive Parameter Resolution (parent)
- **TASK-055-FIX-3**: ParameterStore Context Truncation (previous fix)
- **TASK-041**: Router YAML Workflow Integration (conditional steps)

---

## Notes

This bug only affects workflows executed via `router_set_goal` → `execute_pending_workflow()`. Direct workflow expansion via `expand_workflow()` works correctly because it passes parameters properly (registry.py line 254).

The bug was introduced when `execute_pending_workflow()` was added for TASK-055 but didn't replicate the full parameter passing logic from `expand_workflow()`.
