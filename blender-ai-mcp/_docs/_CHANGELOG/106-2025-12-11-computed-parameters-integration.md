# Changelog Entry #100: Computed Parameters Integration in WorkflowRegistry

**Date**: 2025-12-11
**Type**: Enhancement
**Component**: Router / Workflows
**Related Tasks**: TASK-055-FIX-7 (Phase 0), TASK-056-5

---

## Overview

Integrated TASK-056-5 computed parameters into `WorkflowRegistry.expand_workflow()` to enable auto-calculated parameter values in YAML workflows. This was the missing link that prevented computed parameters from working despite being fully implemented in `ExpressionEvaluator`.

---

## Changes Made

### 1. WorkflowRegistry Integration

**File**: `server/router/application/workflows/registry.py` (lines 252-282)

**Implementation**:
```python
# TASK-055-FIX-7 Phase 0: Resolve computed parameters
if definition.parameters:
    try:
        # Separate explicit params (from params arg) and base params (defaults + modifiers)
        explicit_params = params or {}
        base_params = {k: v for k, v in all_params.items() if k not in explicit_params}

        # Resolve computed parameters using all available params
        computed_values = self._evaluator.resolve_computed_parameters(
            schemas, all_params
        )

        # Merge: base_params < computed_values < explicit_params
        # Computed params override defaults but NOT explicit params
        all_params = {**base_params, **computed_values, **explicit_params}

        logger.debug(
            f"Resolved {len(computed_values)} computed parameters for "
            f"'{workflow_name}': {list(computed_values.keys())}"
        )
    except ValueError as e:
        # Circular dependency or missing required variable
        logger.error(
            f"Computed parameter dependency error in '{workflow_name}': {e}"
        )
        # Continue without computed params - workflow may fail later with clearer error
    except Exception as e:
        # Syntax error, unexpected exception
        logger.error(
            f"Unexpected error resolving computed parameters in '{workflow_name}': {e}"
        )
        # Continue without computed params
```

**Key Features**:
- ✅ Calls `ExpressionEvaluator.resolve_computed_parameters()` with topological sorting
- ✅ Explicit params override computed params (priority: base < computed < explicit)
- ✅ Graceful degradation on errors (logs error, workflow continues)
- ✅ Debug logging for resolved parameters

### 2. Unit Tests

**File**: `tests/unit/router/application/workflows/test_registry.py` (lines 262-400)

**3 New Tests**:

1. **`test_expand_workflow_with_computed_parameters`** (lines 264-318):
   - Tests basic computed parameter resolution
   - Validates dependency chain: `table_width` → `plank_count` → `plank_actual_width`
   - Verifies: `plank_count = ceil(0.8 / 0.10) = 8`, `plank_actual_width = 0.8 / 8 = 0.1`

2. **`test_expand_workflow_computed_params_circular_dependency`** (lines 320-354):
   - Tests graceful handling of circular dependencies (`a → b → a`)
   - Verifies workflow still expands (no crash)
   - Logs error but continues execution

3. **`test_expand_workflow_computed_params_explicit_override`** (lines 356-400):
   - Tests that explicit params override computed params
   - Without override: `plank_count = ceil(0.8 / 0.1) = 8`
   - With override: `plank_count = 10` (explicit value wins)

**Test Results**: ✅ All 26 tests passing (including 3 new Phase 0 tests)

---

## Use Case Example

**Before Phase 0** (BROKEN):
```yaml
parameters:
  plank_count:
    type: int
    computed: "ceil(table_width / plank_max_width)"
    depends_on: ["table_width", "plank_max_width"]

steps:
  - tool: modeling_transform_object
    params:
      scale: ["$plank_actual_width", 1.0, 0.1]  # ❌ ERROR: plank_actual_width undefined
```

**After Phase 0** (WORKS):
```yaml
parameters:
  plank_count:
    type: int
    computed: "ceil(table_width / plank_max_width)"
    depends_on: ["table_width", "plank_max_width"]

  plank_actual_width:
    type: float
    computed: "table_width / plank_count"
    depends_on: ["table_width", "plank_count"]

steps:
  - tool: modeling_transform_object
    params:
      scale: ["$plank_actual_width", 1.0, 0.1]  # ✅ WORKS: 0.1 (for 0.8m width)
```

---

## Benefits

1. **Cleaner YAML**: No repeated complex expressions
   - Before: `$CALCULATE(table_width / ceil(table_width / plank_max_width))` × 15 times
   - After: `$plank_actual_width` (computed once, used 15 times)

2. **Better Performance**: Computed once vs. evaluated 15+ times per workflow

3. **Type Safety**: `plank_count` validated as `int` (automatic rounding via `ceil()`)

4. **Maintainability**: Formula defined once in `parameters` section

5. **Dependency Awareness**: Topological sorting ensures correct evaluation order

---

## Clean Architecture Compliance

✅ **No violations**:
- Domain layer: `ParameterSchema` already has `computed` and `depends_on` fields
- Application layer: `ExpressionEvaluator.resolve_computed_parameters()` already implemented
- Application layer: `WorkflowRegistry.expand_workflow()` now calls the evaluator
- Infrastructure layer: `WorkflowLoader` already parses computed params from YAML

**Dependencies flow correctly**: Infrastructure → Application → Domain

---

## Next Steps

Phase 0 is complete. Next:
- **Phase 1-3**: Update `simple_table.yaml` to use computed parameters for dynamic plank system
  - Rename parameters: `leg_offset_x`, `leg_offset_y`
  - Add computed params: `plank_count`, `plank_actual_width`
  - Replace 5 fixed planks with 15 conditional planks

---

## Related Documentation

- **TASK-055-FIX-7**: Dynamic Plank System (Phase 0 completed)
- **TASK-056-5**: Computed Parameters (implementation)
- **Test Coverage**: `_docs/_TESTS/README.md` (Router subsystems table)

---

## Test Command

```bash
PYTHONPATH=. poetry run pytest tests/unit/router/application/workflows/test_registry.py::TestWorkflowRegistryWithYAML -v
```

**Expected**: 10 tests pass (including 3 new Phase 0 tests)

---

## Lines Changed

- **`registry.py`**: 31 lines added (252-282)
- **`test_registry.py`**: 139 lines added (262-400)
- **Total**: 170 lines

---

## Impact

- ✅ All existing workflows continue to work (backward compatible)
- ✅ Workflows can now use computed parameters from YAML
- ✅ Graceful error handling (no breaking changes)
- ✅ Clean Architecture maintained
- ✅ Comprehensive test coverage (3 new tests)
