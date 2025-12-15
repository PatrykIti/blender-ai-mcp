# 107 - 2025-12-11: Dynamic Plank System for simple_table.yaml

**Status**: ✅ Completed
**Type**: Feature Enhancement + Bug Fix
**Task**: TASK-055-FIX-7 Phase 1-3
**Complexity**: Medium (2 hours implementation)

---

## Overview

Complete rewrite of `simple_table.yaml` workflow with:
1. **Parameter Renaming**: `leg_offset_from_beam` → `leg_offset_x`, `leg_offset_from_beam_lengthwise` → `leg_offset_y`
2. **Dynamic Plank System**: 5 fixed planks → 15 conditional planks with computed parameters
3. **Fractional Plank Support**: Adapts plank width to fit any table width exactly
4. **Critical Bug Fix**: Set evaluator context with computed parameters for $CALCULATE expressions

---

## Changes Made

### 1. `simple_table.yaml` - Complete Rewrite (556 lines, version 2.0.0)

**Parameter Renaming**:
```yaml
# OLD
leg_offset_from_beam: 0.05
leg_offset_from_beam_lengthwise: 0.05

# NEW
leg_offset_x: 0.05  # Distance from crossbeam edge in X axis (width)
leg_offset_y: 0.05  # Distance from crossbeam edge in Y axis (length)
```

**Computed Parameters Added** (TASK-056-5):
```yaml
plank_count:
  type: int
  computed: "ceil(table_width / plank_max_width)"
  depends_on: ["table_width", "plank_max_width"]
  description: Number of planks needed (auto-calculated based on table width and max plank width)

plank_actual_width:
  type: float
  computed: "table_width / plank_count"
  depends_on: ["table_width", "plank_count"]
  description: Actual width of each plank (adapted to fit table width exactly)
```

**Dynamic Plank System**:
- **OLD**: 5 fixed planks with hardcoded widths
- **NEW**: 15 conditional planks with `condition: "plank_count >= N"`
- Each plank uses `$plank_actual_width` for clean, readable scaling
- Supports fractional widths (e.g., 0.83m → 9 planks × 0.0922m each)

**Leg Formulas Updated** (4 legs):
```yaml
# OLD
location: [
  "$CALCULATE(-(table_width * 0.65 / 2 - leg_offset_from_beam))",
  "$CALCULATE(-(table_length * 0.926 / 2 - leg_offset_from_beam_lengthwise))",
  "$CALCULATE(leg_length / 2)"
]

# NEW
location: [
  "$CALCULATE(-(table_width * 0.65 / 2 - leg_offset_x))",
  "$CALCULATE(-(table_length * 0.926 / 2 - leg_offset_y))",
  "$CALCULATE(leg_length / 2)"
]
```

### 2. `registry.py` - Critical Bug Fix (3 lines added)

**Problem**: Computed parameters were resolved but not available to $CALCULATE expressions.

**Root Cause**: `ExpressionEvaluator` context wasn't updated with computed parameters before resolving step params.

**Fix** (lines 289-291):
```python
# Set evaluator context with all resolved parameters (including computed)
# This allows $CALCULATE expressions to reference computed params
self._evaluator.set_context(all_params)

steps = self._resolve_definition_params(definition.steps, all_params)
```

**Error Before Fix**:
```
Expression evaluation failed: '-table_width / 2 + plank_actual_width / 2'
- Unknown variable: plank_actual_width
Failed to evaluate $CALCULATE, returning original:
$CALCULATE(-table_width / 2 + plank_actual_width / 2)
```

**Result After Fix**: All $CALCULATE expressions evaluate successfully with computed parameters.

### 3. Test Script Created

**File**: `test_simple_table_workflow.py` (116 lines)

Tests 4 table widths:
- 0.8m → 8 planks × 0.10m each
- 0.45m → 5 planks × 0.09m each
- 1.2m → 12 planks × 0.10m each
- 0.83m → 9 planks × 0.0922m each

**All tests passing** ✅

---

## Technical Details

### Flow of Computed Parameter Resolution

**Before Fix** (BROKEN):
```
WorkflowRegistry.expand_workflow()
  → resolve_computed_parameters() [plank_count, plank_actual_width calculated]
  → all_params = {..., plank_count: 8, plank_actual_width: 0.1}
  → _resolve_definition_params()  [tries to use computed params]
    → ExpressionEvaluator.resolve_param_value()
      → evaluator.context = {}  ❌ Empty context!
      → ERROR: Unknown variable: plank_actual_width
```

**After Fix** (WORKING):
```
WorkflowRegistry.expand_workflow()
  → resolve_computed_parameters() [plank_count, plank_actual_width calculated]
  → all_params = {..., plank_count: 8, plank_actual_width: 0.1}
  → self._evaluator.set_context(all_params)  ✅ NEW!
  → _resolve_definition_params()  [uses computed params]
    → ExpressionEvaluator.resolve_param_value()
      → evaluator.context = {plank_count: 8, plank_actual_width: 0.1}  ✅
      → SUCCESS: Evaluates expressions correctly
```

### Benefits of Computed Parameters

**Before** (repeated 30 times across 15 planks):
```yaml
condition: "ceil(table_width / plank_max_width) >= N"
scale: ["$CALCULATE(table_width / ceil(table_width / plank_max_width))", ...]
```
- ❌ 30+ redundant `ceil()` calculations
- ❌ Verbose, error-prone expressions
- ❌ Hard to read and maintain

**After** (defined once, used 30 times):
```yaml
condition: "plank_count >= N"
scale: ["$plank_actual_width", ...]
```
- ✅ Calculated once, reused 30+ times (performance)
- ✅ Clean, readable variable references
- ✅ Type-safe (int vs float validated)
- ✅ Easy to modify formula in one place

---

## Testing Results

### Test Output (All Passed)

```
============================================================
TASK-055-FIX-7: Simple Table Workflow Test
Testing dynamic plank system with computed parameters
============================================================

Testing table_width = 0.8m
✅ Workflow expanded: 28 total steps
✅ Plank count (transform steps): 8
✅ Plank count matches expected: 8
✅ All planks have uniform width: 0.1000m
✅ Width matches computed plank_actual_width

Testing table_width = 0.45m
✅ Workflow expanded: 22 total steps
✅ Plank count (transform steps): 5
✅ Plank count matches expected: 5
✅ All planks have uniform width: 0.0900m
✅ Width matches computed plank_actual_width

Testing table_width = 1.2m
✅ Workflow expanded: 36 total steps
✅ Plank count (transform steps): 12
✅ Plank count matches expected: 12
✅ All planks have uniform width: 0.1000m
✅ Width matches computed plank_actual_width

Testing table_width = 0.83m
✅ Workflow expanded: 30 total steps
✅ Plank count (transform steps): 9
✅ Plank count matches expected: 9
✅ All planks have uniform width: 0.0922m
✅ Width matches computed plank_actual_width

TEST SUMMARY
✅ PASS - table_width = 0.8m
✅ PASS - table_width = 0.45m
✅ PASS - table_width = 1.2m
✅ PASS - table_width = 0.83m

Total: 4/4 tests passed
```

### Verification of Computed Parameters

| Table Width | Computed plank_count | Computed plank_actual_width | Planks Created | Result |
|-------------|---------------------|----------------------------|----------------|---------|
| 0.8m | `ceil(0.8/0.1) = 8` | `0.8/8 = 0.1000m` | 8 | ✅ Perfect fit |
| 0.45m | `ceil(0.45/0.1) = 5` | `0.45/5 = 0.0900m` | 5 | ✅ Fractional |
| 1.2m | `ceil(1.2/0.1) = 12` | `1.2/12 = 0.1000m` | 12 | ✅ Perfect fit |
| 0.83m | `ceil(0.83/0.1) = 9` | `0.83/9 = 0.0922m` | 9 | ✅ Fractional |

---

## Files Changed

| File | Lines Changed | Type |
|------|--------------|------|
| `server/router/application/workflows/custom/simple_table.yaml` | 556 lines (rewrite) | Feature |
| `server/router/infrastructure/workflow_loader.py` | +3 lines (289-291) | Bug Fix |
| `test_simple_table_workflow.py` | 116 lines (new) | Test |
| `_docs/_TASKS/TASK-055-FIX-7_Dynamic_Plank_System_Simple_Table.md` | Updated status | Documentation |

**Total**: ~675 lines changed

---

## Clean Architecture Compliance

**Layers Modified**:
- ✅ **Application Layer**: `WorkflowRegistry.expand_workflow()` - added evaluator context update
- ✅ **Infrastructure Layer**: `simple_table.yaml` - workflow definition rewrite
- ✅ **No violations**: Application layer calls its own methods correctly

**Dependency Rule Check**:
```
Application → Domain ✅ (WorkflowRegistry uses ParameterSchema)
Application → Infrastructure ❌ (No dependency on WorkflowLoader)
Infrastructure → Domain ✅ (YAML uses ParameterSchema structure)
```

All dependencies point INWARD correctly. ✅

---

## Usage Example

### Before (Fixed Planks)
```python
registry = WorkflowRegistry()
calls = registry.expand_workflow("simple_table_workflow", params={"table_width": 0.83})
# Result: 5 planks × 0.166m each (unrealistic wide planks)
```

### After (Dynamic Planks)
```python
registry = WorkflowRegistry()
calls = registry.expand_workflow("simple_table_workflow", params={"table_width": 0.83})
# Result: 9 planks × 0.0922m each (realistic fractional planks)
# Computed automatically: plank_count = ceil(0.83 / 0.1) = 9
#                         plank_actual_width = 0.83 / 9 = 0.0922m
```

---

## Impact

**Performance**:
- ✅ Computed parameters calculated once (vs 30+ times previously)
- ✅ Workflow expansion faster for wide tables

**Maintainability**:
- ✅ Clean variable references: `$plank_actual_width` vs `$CALCULATE(table_width / ceil(...))`
- ✅ Easy to modify plank logic in one place
- ✅ Self-documenting parameter definitions

**Correctness**:
- ✅ Fractional plank widths work correctly
- ✅ Any table width (0.2m - 1.5m) creates realistic planks
- ✅ No more unrealistically wide planks

**Robustness**:
- ✅ Bug fix ensures computed params work in all $CALCULATE expressions
- ✅ Type safety: `plank_count` validated as int
- ✅ Dependency order resolved automatically (topological sort)

---

## Related Changes

- **Changelog #106** (2025-12-11): Phase 0 - Computed parameters integration in `WorkflowRegistry`
- **TASK-055-FIX-7**: Now fully completed (Phase 0 + Phase 1-3)
- **TASK-056-5**: Computed parameters feature now battle-tested in production workflow

---

## Notes

- This completes TASK-055-FIX-7 entirely (all phases done)
- Critical bug discovered during Phase 1-3 testing (evaluator context not set)
- Bug fix in Phase 0 code (registry.py) required to make Phase 1-3 work
- Test script created for regression testing (`test_simple_table_workflow.py`)
- Maximum 15 planks covers table widths up to 1.5m (parameter range limit)
