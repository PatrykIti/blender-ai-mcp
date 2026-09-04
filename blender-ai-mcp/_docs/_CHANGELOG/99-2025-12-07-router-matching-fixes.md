# 99 - Router Matching & Parametric Variables Fixes

**Date:** 2025-12-07
**Task:** TASK-051, TASK-052 Bug Fixes
**Status:** ✅ Done

---

## Summary

Fixed critical bugs in Router Supervisor that prevented parametric variables (TASK-052) and confidence-based workflow adaptation (TASK-051) from working correctly.

---

## Changes

### 1. Parametric Variables Not Applied (TASK-052 Fix)

**Problem:** When user said "picnic table with straight legs", the `modifiers` section in YAML was not being applied - legs were still angled.

**Root Cause:**
- `user_prompt` was not passed to `registry.expand_workflow()`
- Adapted workflow steps were not getting variable substitution

**Fix in `server/router/application/router.py`:**

```python
# Line 536: Added user_prompt parameter to standard expansion
calls = registry.expand_workflow(
    workflow_name, params, eval_context, user_prompt=self._current_goal or ""
)

# Lines 504-518: Added variable substitution for adapted workflows
variables = self._build_variables(definition, self._current_goal or "")
for i, step in enumerate(adapted_steps):
    resolved_params = self._resolve_step_params(step.params, variables, eval_context)
    # ...
```

**New methods added:**
- `_build_variables()` - Builds variable context from defaults and modifiers
- `_resolve_step_params()` - Resolves `$variable` references in step params
- `_resolve_single_value()` - Handles single value resolution including lists

### 2. Keyword Match Not Creating MatchResult (TASK-051 Fix)

**Problem:** When user said "simple table with 4 legs", the workflow adapter couldn't work because `_last_match_result` was `None` for keyword matches.

**Root Cause:**
- `MatchResult` was only created for semantic matches
- Keyword matches bypassed the semantic matcher entirely
- No confidence level was set for adaptation

**Fix in `server/router/application/router.py`:**

```python
# Lines 1035-1066: Create MatchResult for keyword matches
if workflow_name:
    # Check if workflow has optional steps
    definition = registry.get_definition(workflow_name)
    has_optional = definition and any(s.optional for s in definition.steps)

    # Detect "simple" keywords for LOW confidence
    goal_lower = goal.lower()
    wants_simple = any(kw in goal_lower for kw in [
        "simple", "basic", "minimal", "just", "only", "plain",
        "prosty", "podstawowy", "tylko"  # Polish
    ])

    if wants_simple and has_optional:
        confidence_level = "LOW"
        requires_adaptation = True
    else:
        confidence_level = "HIGH"
        requires_adaptation = has_optional

    self._last_match_result = MatchResult(
        workflow_name=workflow_name,
        confidence=1.0 if not wants_simple else 0.7,
        match_type="keyword",
        confidence_level=confidence_level,
        requires_adaptation=requires_adaptation,
    )
```

### 3. Semantic Matcher Not Initialized (Status Fix)

**Problem:** `router_get_status` showed `semantic_matcher: NOT READY` because initialization was lazy and never triggered for keyword matches.

**Root Cause:**
- `_ensure_semantic_initialized()` was only called in `find_similar_workflows()` and `match_workflow_semantic()`
- Keyword matches in `set_current_goal()` bypassed these methods

**Fix in `server/router/application/router.py`:**

```python
def set_current_goal(self, goal: str) -> Optional[str]:
    self._current_goal = goal

    # Ensure semantic matcher is initialized (eager init on first goal)
    self._ensure_semantic_initialized()

    # Step 1: Try exact keyword match
    # ...
```

---

## Files Modified

| File | Changes |
|------|---------|
| `server/router/application/router.py` | Added `_build_variables()`, `_resolve_step_params()`, `_resolve_single_value()` methods; Fixed `user_prompt` passing; Added `MatchResult` for keyword matches; Added eager semantic initialization |

---

## Testing

### Before Fix
```
Goal: "picnic table with straight legs"
Result: Legs still angled (0.32 rad) - modifiers not applied
Steps: 55 (full workflow including benches)
```

### After Fix
```
Goal: "picnic table with straight legs"
Result: Legs vertical (0 rad) - "straight legs" modifier applied
Steps: 55 (full workflow)

Goal: "simple table with 4 legs"
Result: Core steps only, no benches
Steps: ~20 (CORE_ONLY adaptation)
```

---

## Related

- [97-2025-12-07-confidence-based-workflow-adaptation.md](./97-2025-12-07-confidence-based-workflow-adaptation.md)
- [98-2025-12-07-parametric-variables.md](./98-2025-12-07-parametric-variables.md)
- `_docs/_ROUTER/IMPLEMENTATION/32-workflow-adapter.md`
- `_docs/_ROUTER/IMPLEMENTATION/33-parametric-variables.md`
