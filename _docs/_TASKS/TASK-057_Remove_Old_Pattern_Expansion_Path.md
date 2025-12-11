# Plan: Remove Old Pattern-Based Expansion Path (TASK-057)

## Context

The router currently has TWO expansion paths:
1. **NEW PATH (Triggered)**: `_check_workflow_trigger()` → `triggerer.determine_workflow()` → `_expand_triggered_workflow()` ✅ ACTIVELY USED
2. **OLD PATH (Pattern-based)**: `_expand_workflow()` → `expansion_engine.expand()` ❌ DEAD CODE

The old path is **completely unreachable** regardless of whether `router_set_goal()` is called:

### With `router_set_goal()`:
- `_pending_workflow` is set (router.py:447)
- `_check_workflow_trigger()` returns pending workflow (line 451)
- `triggered_workflow` is not None → line 216 executes
- Line 219 `_expand_workflow()` is never reached

### Without `router_set_goal()`:
- `_pending_workflow` is None
- `triggerer.determine_workflow()` checks (triggerer.py:142-158):
  - Priority 2: Pattern-suggested workflow (line 148-150) → returns workflow
  - Priority 3: Heuristic detection (line 153-156) → returns workflow
- If pattern OR heuristic matches, `triggered_workflow` is not None → line 216 executes
- If neither matches, `triggered_workflow` is None → line 219 executes
- BUT `expansion_engine.expand()` also checks pattern (expansion_engine.py:176-180)
- Without pattern, it returns None → no expansion anyway

**Conclusion**: `_expand_workflow()` at line 219 is **completely dead code** - either unreachable or does nothing.

## What to Remove

### 1. Dead Code in router.py

**File**: `server/router/application/router.py`

**Remove**:
- Line 219: Call to `_expand_workflow()` in the pipeline
- Lines 391-419: The `_expand_workflow()` method itself
- Line 218-219: The `elif not override_result:` condition that calls it

**Simplify**:
```python
# BEFORE (lines 214-219):
expanded = None
if triggered_workflow:
    expanded = self._expand_triggered_workflow(triggered_workflow, params, context)
elif not override_result:
    expanded = self._expand_workflow(tool_name, params, context, pattern)  # DEAD

# AFTER:
expanded = None
if triggered_workflow:
    expanded = self._expand_triggered_workflow(triggered_workflow, params, context)
```

### 2. Dead Code in WorkflowExpansionEngine

**File**: `server/router/application/engines/workflow_expansion_engine.py`

**Remove**:
- Lines 152-181: The `expand()` method (pattern-based expansion)
- Any imports/dependencies only used by `expand()`

**Keep**:
- `expand_workflow()` method (lines 240-267) - still used by `_expand_triggered_workflow()`
- All other methods used by triggered path

### 3. Remove Dead Tests

**Files to remove completely**:
- Any tests specifically testing `_expand_workflow()` method
- Any tests specifically testing `expansion_engine.expand()` method

**Tests to update**:
- `tests/unit/router/application/test_supervisor_router.py` - remove tests for old path
- `tests/unit/router/application/test_workflow_expansion_engine.py` - remove tests for `expand()`

### 4. Update Documentation

**Files to update**:
- `_docs/_ROUTER/IMPLEMENTATION/15-supervisor-router.md` - remove references to old path
- `_docs/_ROUTER/ROUTER_ARCHITECTURE.md` - update pipeline diagram
- `_docs/_TASKS/TASK-057_Remove_Old_Pattern_Expansion_Path.md` - create task file

## What to KEEP (Still Used)

### Critical: These are NOT dead code

**Keep in router.py**:
- `interceptor.intercept()` call (line 192) - still captures tool metadata ✅
- `_check_workflow_trigger()` (line 205-207) - finds triggered workflows ✅
- `_expand_triggered_workflow()` (line 217) - expands triggered workflows ✅
- Pattern detection pipeline - still used by ensemble matcher ✅

**Keep in WorkflowExpansionEngine**:
- `expand_workflow()` method - called by `_expand_triggered_workflow()` ✅
- All workflow transformation logic ✅

**Keep in Ensemble Matcher**:
- `PatternMatcher` component - used in ensemble (15% weight) ✅
- `EnsembleAggregator` ✅
- `ModifierExtractor` ✅

**Keep all tests for**:
- `tool_interceptor.py` - still active ✅
- `_expand_triggered_workflow()` - still active ✅
- `expansion_engine.expand_workflow()` - still active ✅
- Ensemble matcher components ✅

## Implementation Steps

### Step 1: Remove Dead Method Calls
- Remove line 219 in `router.py`: `expanded = self._expand_workflow(...)`
- Simplify conditional at lines 214-219

### Step 2: Remove Dead Methods
- Delete `_expand_workflow()` method from `router.py` (lines 391-419)
- Delete `expand()` method from `workflow_expansion_engine.py` (lines 152-181)

### Step 3: Clean Up Tests
- Identify and remove tests for `_expand_workflow()` in test_supervisor_router.py
- Identify and remove tests for `expand()` in test_workflow_expansion_engine.py
- Verify remaining tests still pass

### Step 4: Update Documentation
- Update router architecture docs to show only triggered path
- Create TASK-057 completion doc
- Update changelog

### Step 5: Verify No Regressions
- Run full test suite: `PYTHONPATH=. poetry run pytest -v`
- Test router with real workflows
- Confirm ensemble matcher still works

## Rationale

### Why This is Safe

1. **Usage Analysis**:
   - `_expand_workflow()` only called at line 219
   - Line 219 only reached when `not triggered_workflow`
   - We **always** call `router_set_goal()` before tool execution
   - Therefore `triggered_workflow` is always set
   - Therefore line 219 is never reached

2. **No Impact on Active Features**:
   - Ensemble matcher (TASK-053) uses `PatternMatcher` internally ✅
   - Triggered expansion (TASK-051, 052, 055) uses `expand_workflow()` ✅
   - Tool interception still works ✅
   - Pattern detection still works (for ensemble) ✅

3. **Simplification Benefits**:
   - Removes confusing dual-path logic
   - Makes router pipeline clearer
   - Reduces maintenance burden
   - Eliminates dead code

### Why Pattern Matcher is Not Affected

The `PatternMatcher` component in the ensemble is **NOT** the same as the old pattern-based expansion path:

| Component | Purpose | Status |
|-----------|---------|--------|
| `GeometryPatternDetector` | Detects scene patterns | ✅ KEEP (used by ensemble) |
| `PatternMatcher` (ensemble) | Scores workflow match based on pattern | ✅ KEEP (15% weight in ensemble) |
| `WorkflowExpansionEngine.expand()` | Expands based on pattern suggestion | ❌ REMOVE (dead code) |
| `router._expand_workflow()` | Calls expansion engine | ❌ REMOVE (never called) |

## Success Criteria

- [ ] All calls to `_expand_workflow()` removed from router.py
- [ ] `_expand_workflow()` method deleted from router.py
- [ ] `expand()` method deleted from workflow_expansion_engine.py
- [ ] Dead tests removed
- [ ] All remaining tests pass
- [ ] Documentation updated
- [ ] TASK-057 marked complete

## Files to Modify

| File | Action | Lines |
|------|--------|-------|
| `server/router/application/router.py` | Remove method call | 219 |
| `server/router/application/router.py` | Delete method | 391-419 |
| `server/router/application/engines/workflow_expansion_engine.py` | Delete method | 152-181 |
| `tests/unit/router/application/test_supervisor_router.py` | Remove tests | TBD |
| `tests/unit/router/application/test_workflow_expansion_engine.py` | Remove tests | TBD |
| `_docs/_ROUTER/IMPLEMENTATION/15-supervisor-router.md` | Update docs | - |
| `_docs/_TASKS/TASK-057_Remove_Old_Pattern_Expansion_Path.md` | Create task | - |

## Risk Assessment

**Low Risk**:
- Code is provably dead (unreachable)
- No active features depend on it
- Ensemble matcher uses different code path
- All tests will verify no regressions

**Mitigation**:
- Run full test suite before and after
- Keep git history for easy rollback if needed
- Document what was removed and why

## Task File Creation

Create new task file: `_docs/_TASKS/TASK-057_Remove_Old_Pattern_Expansion_Path.md`

**Content**:
```markdown
# TASK-057: Remove Old Pattern-Based Expansion Path

**Status**: 🔲 To Do
**Priority**: Medium
**Category**: Router / Code Cleanup

## Objective

Remove the old pattern-based workflow expansion path (`_expand_workflow()` and `expansion_engine.expand()`) which is dead code since we always use `router_set_goal()` triggered workflows.

## Background

The router has two expansion paths:
1. **NEW (Triggered)**: `router_set_goal()` → ensemble matcher → `_expand_triggered_workflow()` ✅ ACTIVE
2. **OLD (Pattern-based)**: pattern detection → `_expand_workflow()` → `expansion_engine.expand()` ❌ DEAD

Since we always call `router_set_goal()` before tool execution, the `triggered_workflow` is always set, making the old path unreachable (router.py:219).

## Implementation Steps

1. **Remove dead method calls** (router.py:219)
2. **Delete dead methods**:
   - `router._expand_workflow()` (lines 391-419)
   - `expansion_engine.expand()` (lines 152-181)
3. **Clean up tests** for removed methods
4. **Update documentation** to reflect single expansion path

## Files to Modify

- `server/router/application/router.py`
- `server/router/application/engines/workflow_expansion_engine.py`
- `tests/unit/router/application/test_supervisor_router.py`
- `tests/unit/router/application/test_workflow_expansion_engine.py`
- `_docs/_ROUTER/IMPLEMENTATION/15-supervisor-router.md`

## Success Criteria

- Dead code removed
- All tests pass
- Documentation updated
- No regression in triggered workflow expansion

## Related Tasks

- TASK-039: Router Supervisor Implementation
- TASK-053: Ensemble Matcher System
```
