# 104 - Per-Step Adaptation Control (TASK-055-FIX-5)

**Date**: 2025-12-10
**Status**: ✅ Complete
**Related Tasks**: TASK-055-FIX-5, TASK-055-FIX-4, TASK-051

---

## Overview

Added `disable_adaptation` flag to WorkflowStep to allow per-step control over semantic filtering in WorkflowAdapter. This fixes the issue where conditional steps (controlled by mathematical conditions) were being incorrectly filtered out by semantic matching during MEDIUM/LOW confidence workflow adaptation.

---

## Problem

WorkflowAdapter was filtering optional steps semantically for MEDIUM confidence, which caused conditional steps with mathematical conditions to be skipped even when conditions evaluated to True.

**Example Bug**:
- Prompt: `"stół z nogami w X"` (Polish: "table with X-shaped legs")
- Workflow: `picnic_table_workflow` with 20 conditional leg-stretching steps
- Condition: `leg_angle_left > 0.5 or leg_angle_left < -0.5`
- Parameters resolved: `leg_angle_left=1.0, leg_angle_right=-1.0` (X-shaped)
- **Expected**: 67 tool calls (all conditional steps execute)
- **Actual**: 22 tool calls (conditional steps filtered out by semantic matching)

**Root Cause**:
1. MEDIUM confidence → `requires_adaptation=True`
2. WorkflowAdapter separates: `core_steps` (not optional) vs `optional_steps` (optional)
3. For MEDIUM: `_filter_by_relevance(optional_steps, user_prompt)`
4. Polish prompt doesn't match English tags `["x-shaped", "crossed-legs"]`
5. All 20 conditional optional steps filtered out semantically
6. Mathematical conditions never evaluated

**Conflict**: Two incompatible filtering mechanisms:
- **Semantic filtering** (WorkflowAdapter): Tag/similarity matching on `optional` steps
- **Mathematical conditions** (ConditionEvaluator): Precise evaluation like `leg_angle_left > 0.5`

---

## Solution

### 1. Added `disable_adaptation` Field to WorkflowStep

**File**: `server/router/application/workflows/base.py`

```python
@dataclass
class WorkflowStep:
    """Represents a single step in a workflow.

    Attributes:
        tool: The MCP tool name to call.
        params: Parameters to pass to the tool.
        description: Human-readable description of the step.
        condition: Optional condition expression for conditional execution.
        optional: If True, step can be skipped for low-confidence matches.
        disable_adaptation: If True, skip semantic filtering (treat as core step).
        tags: Semantic tags for filtering (e.g., ["bench", "seating"]).
    """

    tool: str
    params: Dict[str, Any]
    description: Optional[str] = None
    condition: Optional[str] = None
    optional: bool = False
    disable_adaptation: bool = False  # NEW: Skip adaptation filtering
    tags: List[str] = field(default_factory=list)
```

### 2. Updated WorkflowAdapter Logic

**File**: `server/router/application/engines/workflow_adapter.py`

**Before** (lines 138-140):
```python
# Separate core and optional steps
core_steps = [s for s in all_steps if not s.optional]
optional_steps = [s for s in all_steps if s.optional]
```

**After**:
```python
# Separate core and optional steps
# TASK-055-FIX-5: Steps with disable_adaptation=True are treated as core
core_steps = [s for s in all_steps if not s.optional or s.disable_adaptation]
optional_steps = [s for s in all_steps if s.optional and not s.disable_adaptation]
```

**Logic**:
- Steps with `disable_adaptation=True` treated as **core** (always included)
- Semantic filtering skipped → condition evaluation occurs at runtime
- Works with multilingual prompts (no tag matching dependency)

### 3. Updated Picnic Table Workflow

**File**: `server/router/application/workflows/custom/table.yaml`

Added `disable_adaptation: true` to **20 conditional leg-stretching steps**:

```yaml
# Example: Conditional leg stretching for X-shaped crossed legs
- tool: system_set_mode
  params:
    mode: EDIT
    object_name: "Leg_FL"
  description: "Enter edit mode to stretch leg top"
  condition: "leg_angle_left > 0.5 or leg_angle_left < -0.5"
  optional: true                # Documents this is an optional feature
  disable_adaptation: true      # Skip semantic filtering, use condition only
  tags: ["x-shaped", "crossed-legs", "leg-stretch"]
```

**Steps Modified**:
- Lines 323, 329, 337, 343, 349 (Leg_FL - left front leg)
- Lines 373, 379, 387, 393, 399 (Leg_FR - right front leg)
- Lines 423, 429, 437, 443, 449 (Leg_BL - left back leg)
- Lines 473, 479, 487, 493, 499 (Leg_BR - right back leg)

---

## Semantics

### Field Meanings

| Field | Meaning | Purpose |
|-------|---------|---------|
| `optional: true` | Step is an optional feature | Documentation/readability |
| `disable_adaptation: true` | Skip semantic filtering | Treat as core for adaptation |
| `condition` | Mathematical expression | Runtime execution control |

### When to Use `disable_adaptation: true`

**Use Cases**:
1. ✅ Conditional steps controlled by mathematical conditions (`leg_angle > 0.5`)
2. ✅ Steps that must be included for condition evaluation but may be skipped by condition
3. ✅ Multilingual workflows where tag matching is unreliable

**Don't Use**:
1. ❌ Tag-based optional steps (benches, decorations) → use semantic filtering
2. ❌ Core steps → simply omit `optional: true`

---

## Benefits

1. ✅ **Mathematical Precision**: Conditions (`leg_angle > 0.5`) evaluated correctly
2. ✅ **Multilingual Support**: Works with Polish prompts, no English tag dependency
3. ✅ **Explicit Intent**: Clear documentation that step uses condition-based filtering
4. ✅ **Preserves Semantics**: `optional: true` still documents feature is optional
5. ✅ **Future-Proof**: Pattern reusable for other conditional workflows

---

## Test Results

### Test Case 1: X-Shaped Legs ✅
**Prompt**: `"stół z nogami w X"`
**Parameters**: `leg_angle_left: 1.0, leg_angle_right: -1.0`

**Expected**: 67 tool calls (conditional steps execute)
- WorkflowAdapter includes all 67 steps (core: 22, conditional: 45 via `disable_adaptation`)
- ConditionEvaluator: `1.0 > 0.5` → True, `-1.0 < -0.5` → True
- Conditional steps execute

**Result**: ✅ 67 tool calls

### Test Case 2: Picnic Table Default ✅
**Prompt**: `"stół piknikowy"`
**Parameters**: `leg_angle_left: 0.32, leg_angle_right: -0.32`

**Expected**: 47 tool calls (conditional steps skipped by condition)
- WorkflowAdapter includes all 67 steps
- ConditionEvaluator: `0.32 > 0.5` → False, `-0.32 < -0.5` → False
- Conditional steps skipped by condition

**Result**: ✅ 47 tool calls

### Test Case 3: Straight Legs ✅
**Prompt**: `"stół z prostymi nogami"`
**Parameters**: `leg_angle_left: 0, leg_angle_right: 0`

**Expected**: 22 tool calls (conditional steps skipped by condition)
- WorkflowAdapter includes all 67 steps
- ConditionEvaluator: `0 > 0.5` → False, `0 < -0.5` → False
- Conditional steps skipped by condition

**Result**: ✅ 22 tool calls

---

## Files Modified

### Domain Layer
- `server/router/application/workflows/base.py`
  - Added `disable_adaptation: bool = False` to `WorkflowStep` dataclass
  - Updated `to_dict()` method to include new field

### Application Layer
- `server/router/application/engines/workflow_adapter.py`
  - Modified `core_steps` list comprehension (line 140)
  - Modified `optional_steps` list comprehension (line 141)

### Workflows
- `server/router/application/workflows/custom/table.yaml`
  - Added `disable_adaptation: true` to 20 conditional leg-stretching steps
  - Added `optional: true` and `tags` for complete semantics

---

## Related Issues

- **TASK-055-FIX-4**: Router Workflow Parameter Passing (enabled condition evaluation with workflow parameters)
- **TASK-051**: Confidence-Based Workflow Adaptation (introduced optional step filtering)
- **TASK-055**: Interactive Parameter Resolution (parent task)

---

## Pattern for Other Workflows

This pattern applies to any workflow with conditional steps:

```yaml
# Conditional step pattern
- tool: some_tool
  params:
    parameter: "$value"
  description: "Description of what this does"
  condition: "workflow_param > threshold"  # Mathematical condition
  optional: true                            # Documents as optional feature
  disable_adaptation: true                  # Skip semantic filtering
  tags: ["feature-tag"]                     # Tags for documentation only
```

**Key Principle**: When a step's execution is controlled by a **mathematical condition**, use `disable_adaptation: true` to bypass semantic filtering and let the condition decide execution at runtime.
