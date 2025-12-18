# TASK-057: Remove Old Pattern-Based Expansion Path

**Status**: ✅ Done
**Priority**: 🟡 Medium
**Category**: Router / Code Cleanup
**Completed**: 2025-12-11

## Objective

Remove the old pattern-based workflow expansion path (`_expand_workflow()` and `expansion_engine.expand()`) which is dead code that is never reached in the router pipeline.

## Background

The router had two expansion paths:
1. **NEW (Triggered)**: `_check_workflow_trigger()` → `triggerer.determine_workflow()` → `_expand_triggered_workflow()` ✅ ACTIVE
2. **OLD (Pattern-based)**: `_expand_workflow()` → `expansion_engine.expand()` ❌ DEAD CODE

The old path was **completely unreachable** because:
- With `router_set_goal()`: `_pending_workflow` is set → `triggered_workflow` always set → line 219 never reached
- Without `router_set_goal()`: `triggerer.determine_workflow()` returns workflow from pattern/heuristic → `triggered_workflow` set → line 219 never reached
- Even if line 219 was reached, `expansion_engine.expand()` would return None without pattern

## Implementation Completed

### Files Modified

| File | Action | Status |
|------|--------|--------|
| `server/router/application/router.py` | Removed dead method call (line 219) | ✅ |
| `server/router/application/router.py` | Deleted `_expand_workflow()` method | ✅ |
| `server/router/application/engines/workflow_expansion_engine.py` | Deleted `expand()` method | ✅ |
| `server/router/domain/interfaces/i_expansion_engine.py` | Removed `expand()` from interface | ✅ |
| `tests/unit/router/application/test_workflow_expansion_engine.py` | Removed `TestExpand` class (4 tests) | ✅ |
| `tests/unit/router/application/test_workflow_expansion_engine.py` | Removed `test_empty_params` test | ✅ |

### Changes Summary

**router.py**:
- Removed lines 218-219 (`elif not override_result: expanded = self._expand_workflow(...)`)
- Deleted `_expand_workflow()` method (lines 389-417)
- Simplified expansion logic to only use triggered path

**workflow_expansion_engine.py**:
- Deleted `expand()` method (lines 152-181)
- Kept `expand_workflow()` method (still used by triggered path)

**i_expansion_engine.py**:
- Removed abstract `expand()` method from interface
- All other methods preserved

**test_workflow_expansion_engine.py**:
- Removed entire `TestExpand` class:
  - `test_expand_with_pattern_suggestion`
  - `test_expand_no_pattern`
  - `test_expand_pattern_no_workflow`
  - `test_expand_disabled`
- Removed `test_empty_params` from `TestEdgeCases`

## What Was Preserved

### Active Components (NOT removed)

**Keep in router.py**:
- `interceptor.intercept()` call - still captures tool metadata ✅
- `_check_workflow_trigger()` - finds triggered workflows ✅
- `_expand_triggered_workflow()` - expands triggered workflows ✅
- Pattern detection pipeline - still used by ensemble matcher ✅

**Keep in WorkflowExpansionEngine**:
- `expand_workflow()` method - called by `_expand_triggered_workflow()` ✅
- All workflow transformation logic ✅

**Keep in Ensemble Matcher**:
- `PatternMatcher` component - used in ensemble (15% weight) ✅
- `EnsembleAggregator` ✅
- `ModifierExtractor` ✅

## Testing

All tests pass successfully:
- ✅ `test_workflow_expansion_engine.py`: 24 passed
- ✅ `test_supervisor_router.py`: 50 passed, 3 warnings
- ✅ No regressions in router functionality
- ✅ Ensemble matcher still works correctly
- ✅ Triggered workflow expansion still works correctly

## Success Criteria

- [✅] All calls to `_expand_workflow()` removed from router.py
- [✅] `_expand_workflow()` method deleted from router.py
- [✅] `expand()` method deleted from workflow_expansion_engine.py
- [✅] `expand()` abstract method removed from i_expansion_engine.py
- [✅] Dead tests removed (5 total)
- [✅] All remaining tests pass
- [✅] No regression in triggered workflow expansion
- [✅] TASK-057 marked complete in README.md

## Related Tasks

- TASK-039: Router Supervisor Implementation
- TASK-053: Ensemble Matcher System
- TASK-051: Confidence-Based Workflow Adaptation
- TASK-052: Intelligent Parametric Adaptation
