# TASK-055-FIX-6: Flexible YAML Parameter Loading with Semantic Extensions

**Status**: ✅ Done
**Priority**: P0 (Critical - Blocks TASK-055-FIX-5)
**Related**: TASK-055-FIX-5, TASK-055, TASK-051
**Created**: 2025-12-10
**Completed**: 2025-12-10

---

## Problem

After implementing TASK-055-FIX-5 (`disable_adaptation` field), testing revealed **the field is NOT being loaded from YAML**.

**Evidence**:
```
docker logs: "MEDIUM confidence - returning 22 core + 0 relevant optional steps, skipping 45 optional steps"
```

- **Expected**: 67 tool calls (22 core + 45 conditional with `disable_adaptation: true`)
- **Actual**: 22 tool calls (45 conditional steps filtered out)

**Root Cause**:
`WorkflowLoader._parse_step()` in `workflow_loader.py:322-329` hardcodes only 6 fields:
- `tool` ✅
- `params` ✅
- `description` ✅
- `condition` ✅
- `optional` ✅
- `tags` ✅
- `disable_adaptation` ❌ **NOT LOADED**

Even though `disable_adaptation: true` exists in `table.yaml` (20 conditional steps), it's ignored during parsing.

---

## Requirements

### 1. Flexible YAML Loading
Make `WorkflowStep` YAML loading **automatic and future-proof**:
- Load ALL fields that exist in `WorkflowStep` dataclass
- No manual field synchronization required
- New fields added to `WorkflowStep` automatically loaded from YAML

### 2. Dual Parameter Semantics

Distinguish between two types of step parameters:

#### A. **Explicit Logic Parameters** (Handled by Specific Code)
Parameters with dedicated business logic in Router components:
- `disable_adaptation` → Used by `WorkflowAdapter` to skip semantic filtering
- `optional` → Used by `WorkflowAdapter` to determine core vs optional steps
- `condition` → Used by `ConditionEvaluator` for runtime step execution
- `tags` → Used by `WorkflowAdapter._filter_by_relevance()` for semantic matching

#### B. **Semantic Filter Parameters** (Generic Handling)
Custom boolean parameters that act as semantic filters:
- `add_bench: false` → Step skipped when bench not requested
- `include_stretchers: true` → Step included only for tables with stretchers
- `decorative: true` → Step included only for decorative variants

**Key Difference**:
- Explicit parameters have hardcoded logic in Router classes
- Semantic parameters are treated generically as yes/no filters based on user prompt

---

## Proposed Solution

### Phase 1: Flexible Field Loading (Immediate Fix)

**File**: `server/router/infrastructure/workflow_loader.py:299-329`

Replace hardcoded field loading with dynamic dataclass introspection:

```python
import dataclasses

def _parse_step(self, data: Dict[str, Any], index: int, source: Optional[Path] = None) -> WorkflowStep:
    """Parse a single workflow step - flexible version."""

    # Validate required fields
    for field in self.STEP_REQUIRED_FIELDS:  # ["tool", "params"]
        if field not in data:
            raise WorkflowValidationError(...)

    # Extract all WorkflowStep fields dynamically
    step_fields = {f.name: f for f in dataclasses.fields(WorkflowStep)}
    step_data = {}

    # Load each field from YAML if present, otherwise use dataclass default
    for field_name, field_info in step_fields.items():
        if field_name in data:
            step_data[field_name] = data[field_name]
        elif field_info.default is not dataclasses.MISSING:
            step_data[field_name] = field_info.default
        elif field_info.default_factory is not dataclasses.MISSING:
            step_data[field_name] = field_info.default_factory()

    return WorkflowStep(**step_data)
```

**Benefits**:
- ✅ Fixes `disable_adaptation` loading bug immediately
- ✅ Future-proof: new fields auto-loaded
- ✅ Type-safe: respects dataclass defaults
- ✅ Minimal code change

---

### Phase 2: Semantic Filter Parameters (Future Enhancement)

**Goal**: Allow workflow authors to add custom boolean filters without modifying Router code.

**Example YAML**:
```yaml
steps:
  # Core table structure
  - tool: modeling_create_primitive
    params:
      primitive_type: Cube
    description: "Create table top"
    # No semantic filters - always included

  # Optional bench (semantic filter)
  - tool: modeling_create_primitive
    params:
      primitive_type: Cube
    description: "Create bench"
    optional: true
    add_bench: true  # NEW: Semantic filter parameter
    tags: ["bench", "seating"]
```

**Semantic Filter Handling** (in `WorkflowAdapter`):

```python
def _filter_by_relevance(
    self,
    steps: List[WorkflowStep],
    user_prompt: str
) -> List[WorkflowStep]:
    """Filter optional steps by semantic relevance."""

    relevant = []
    for step in steps:
        # Check explicit tags (existing logic)
        if self._matches_tags(step.tags, user_prompt):
            relevant.append(step)
            continue

        # NEW: Check semantic filter parameters
        semantic_params = self._extract_semantic_params(step)
        if self._matches_semantic_params(semantic_params, user_prompt):
            relevant.append(step)

    return relevant

def _extract_semantic_params(self, step: WorkflowStep) -> Dict[str, bool]:
    """Extract custom boolean parameters as semantic filters."""
    EXPLICIT_PARAMS = {"tool", "params", "description", "condition",
                      "optional", "disable_adaptation", "tags"}

    semantic = {}
    for field in dataclasses.fields(step):
        if field.name not in EXPLICIT_PARAMS:
            value = getattr(step, field.name)
            if isinstance(value, bool):
                semantic[field.name] = value

    return semantic

def _matches_semantic_params(
    self,
    semantic_params: Dict[str, bool],
    user_prompt: str
) -> bool:
    """Check if user prompt matches semantic filter conditions."""

    for param_name, param_value in semantic_params.items():
        # Convert snake_case to natural language: "add_bench" -> "bench"
        keyword = param_name.replace("add_", "").replace("include_", "").replace("_", " ")

        if param_value and keyword.lower() in user_prompt.lower():
            return True  # User wants this feature
        elif not param_value and keyword.lower() not in user_prompt.lower():
            return True  # User doesn't want this feature, step correctly excluded

    return False
```

**Benefits**:
- ✅ Workflow authors can add custom filters without code changes
- ✅ Semantic parameters auto-discovered via dataclass introspection
- ✅ Clear separation: explicit logic vs semantic filters
- ✅ Extensible: works for any boolean parameter

---

## Implementation Plan

### Step 1: Fix Immediate Bug (Phase 1)
**File**: `server/router/infrastructure/workflow_loader.py`

1. Add `import dataclasses` at top of file
2. Replace `_parse_step()` method (lines 322-329) with flexible implementation
3. Verify all 7 current WorkflowStep fields are loaded correctly

**Time**: 15 minutes
**Risk**: Low (preserves existing behavior, just makes it flexible)

### Step 2: Test TASK-055-FIX-5 Scenarios
Rebuild Docker image and test:

**Test Case 1: X-shaped legs**
```python
router_set_goal("table with X-shaped legs")
# Provide: leg_angle_left=1.0, leg_angle_right=-1.0
```
- Expected: 67 tool calls ✅
- Verify: `disable_adaptation: true` loaded and respected

**Test Case 2: Picnic table default**
```python
router_set_goal("picnic table")
# Provide: leg_angle_left=0.32, leg_angle_right=-0.32
```
- Expected: 47 tool calls ✅

**Test Case 3: Straight legs**
```python
router_set_goal("table with straight legs")
# Provide: leg_angle_left=0, leg_angle_right=0
```
- Expected: 22 tool calls ✅

### Step 3: Semantic Filter Parameters (Phase 2 - Optional)
**File**: `server/router/application/engines/workflow_adapter.py`

1. Add `_extract_semantic_params()` helper method
2. Add `_matches_semantic_params()` helper method
3. Update `_filter_by_relevance()` to check semantic params
4. Add unit tests for semantic parameter matching

**Time**: 1-2 hours
**Risk**: Medium (new feature, needs thorough testing)

---

## Files to Modify

### Phase 1 (Immediate Fix)
**Primary Change**:
- `server/router/infrastructure/workflow_loader.py`
  - Add `import dataclasses` at top
  - Update `_parse_step()` method (lines 322-329)

**No Changes Needed** (Already Done in TASK-055-FIX-5):
- ✅ `server/router/application/workflows/base.py` - WorkflowStep has `disable_adaptation`
- ✅ `server/router/application/engines/workflow_adapter.py` - Logic respects `disable_adaptation`
- ✅ `server/router/application/workflows/custom/table.yaml` - 20 steps have `disable_adaptation: true`

### Phase 2 (Future Enhancement)
**Optional Changes**:
- `server/router/application/engines/workflow_adapter.py`
  - Add `_extract_semantic_params()` method
  - Add `_matches_semantic_params()` method
  - Update `_filter_by_relevance()` method

---

## Success Criteria

### Phase 1 (Must Have)
- ✅ `disable_adaptation` field loaded from YAML
- ✅ X-shaped legs: 67 tool calls
- ✅ Picnic table: 47 tool calls
- ✅ Straight legs: 22 tool calls
- ✅ Future WorkflowStep fields automatically loaded
- ✅ No manual field synchronization required

### Phase 2 (Nice to Have)
- ✅ Custom boolean parameters work as semantic filters
- ✅ Workflow authors can add filters without code changes
- ✅ Clear separation: explicit logic vs semantic filters
- ✅ Unit tests for semantic parameter matching

---

## Example: Semantic Filter in Action

**YAML Workflow**:
```yaml
parameters:
  add_bench:
    type: boolean
    default: false
    description: "Whether to add a bench to the picnic table"

steps:
  # Core table (always included)
  - tool: modeling_create_primitive
    params:
      primitive_type: Cube
    description: "Create table top"

  # Optional bench (semantic filter)
  - tool: modeling_create_primitive
    params:
      primitive_type: Cube
    description: "Create bench"
    optional: true
    add_bench: true  # Semantic filter: included only if bench requested
    tags: ["bench", "seating"]
```

**User Prompts**:
1. `"picnic table"` → `add_bench: false` (default) → bench step skipped
2. `"picnic table with bench"` → semantic match on "bench" → bench step included
3. `"picnic table with bench"` → semantic match on "bench" → bench step included

**How It Works**:
1. WorkflowAdapter sees `add_bench: true` on bench step
2. Extracts it as semantic filter parameter
3. Checks if user prompt contains "bench" keyword
4. If yes → step included, if no → step skipped

---

## Trade-offs

### Phase 1: Flexible Loading
**Pros**:
- ✅ Fixes immediate bug
- ✅ Future-proof
- ✅ Minimal code change

**Cons**:
- ❌ None (strictly better than hardcoded approach)

### Phase 2: Semantic Filters
**Pros**:
- ✅ Extensible without code changes
- ✅ Workflow authors have more control
- ✅ Natural language matching

**Cons**:
- ❌ More complex logic in WorkflowAdapter
- ❌ Potential for false positives in keyword matching
- ❌ Needs thorough testing

---

## Recommendation

**Implement Phase 1 immediately** to unblock TASK-055-FIX-5.

**Defer Phase 2** until we have:
1. More real-world workflows requiring custom filters
2. Clear patterns emerging from workflow usage
3. Time for proper testing and refinement

---

## Related Issues

- **TASK-055-FIX-5**: Per-Step Adaptation Control (blocked by this fix)
- **TASK-055**: Interactive Parameter Resolution (parent task)
- **TASK-051**: Confidence-Based Workflow Adaptation (introduced optional step filtering)
- **TASK-041**: Router YAML Workflow Integration (original workflow system)

---

## Notes

- Phase 1 is a **bug fix** (critical)
- Phase 2 is a **feature enhancement** (nice to have)
- User explicitly requested flexible approach: *"flexible to parse all parameters from YAML"*
- User wants semantic handling for custom params: *"the rest should be treated semantically"*
- Example use case: `add_bench: false` to skip bench steps when not requested
