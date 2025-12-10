# TASK-055-FIX-5: Per-Step Adaptation Control

**Status**: 🚧 In Progress (Plan Ready)
**Priority**: Critical
**Category**: Enhancement
**Related**: TASK-055-FIX-4 (Router Workflow Parameter Passing)

---

## Problem

WorkflowAdapter filtruje optional steps semantycznie dla MEDIUM/LOW confidence, co powoduje że conditional steps są pomijane mimo że parametry spełniają `condition`.

### Current Behavior

**Workflow**: `picnic_table_workflow` (67 steps total)
- **Core steps** (not optional): 22 steps
- **Optional conditional steps**: 45 steps (leg stretching with `condition`)

**For MEDIUM confidence**:
```python
# WorkflowAdapter lines 139-140
core_steps = [s for s in all_steps if not s.optional]  # 22 steps
optional_steps = [s for s in all_steps if s.optional]  # 45 steps

# Line 157
relevant_optional = self._filter_by_relevance(optional_steps, user_prompt)
```

**Problem**:
- User prompt: `"stół z nogami w X"` (Polish)
- Step tags: `["x-shaped", "crossed-legs", "leg-stretch"]` (English)
- Semantic matching FAILS → 0 relevant optional steps
- Result: 22 tool calls instead of 67 ❌

### Root Cause

Two incompatible filtering mechanisms:
1. **Semantic filtering** (WorkflowAdapter): Tag/similarity matching on `optional` steps
2. **Mathematical conditions** (ConditionEvaluator): `leg_angle_left > 0.5` evaluation

Conditional steps need **condition-based** execution, not semantic filtering.

---

## Solution: `disable_adaptation` Flag

Add per-step flag to skip semantic filtering while preserving `optional` documentation.

### Design

**Workflow YAML**:
```yaml
# Conditional leg stretching - ALWAYS included, condition decides execution
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

**Semantics**:
- `optional: true` → Documents feature is optional (for readability)
- `disable_adaptation: true` → Treats step as **core** for adaptation purposes
- `condition` → Mathematical evaluation at runtime determines execution

**Benefits**:
1. ✅ Preserves semantic meaning of `optional` in YAML
2. ✅ Explicit intent: "don't filter, use condition"
3. ✅ Works with multilingual prompts (no tag matching needed)
4. ✅ Mathematical precision (condition) > semantic approximation (tags)
5. ✅ Future-proof pattern for other conditional workflows

---

## Implementation

### Step 1: Update WorkflowStep Dataclass

**File**: `server/router/application/workflows/base.py`

**Current** (line ~45):
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
        tags: Semantic tags for filtering (e.g., ["bench", "seating"]).
    """

    tool: str
    params: Dict[str, Any]
    description: Optional[str] = None
    condition: Optional[str] = None
    optional: bool = False
    tags: List[str] = field(default_factory=list)
```

**Add** (after `optional` field):
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
    disable_adaptation: bool = False  # NEW: Skip adaptation filtering for conditional steps
    tags: List[str] = field(default_factory=list)
```

### Step 2: Update WorkflowAdapter Logic

**File**: `server/router/application/engines/workflow_adapter.py`

**Current** (lines 138-140):
```python
# Separate core and optional steps
core_steps = [s for s in all_steps if not s.optional]
optional_steps = [s for s in all_steps if s.optional]
```

**Change to**:
```python
# Separate core and optional steps
# TASK-055-FIX-5: Steps with disable_adaptation=True are treated as core
core_steps = [s for s in all_steps if not s.optional or s.disable_adaptation]
optional_steps = [s for s in all_steps if s.optional and not s.disable_adaptation]
```

**Logic**:
- `not s.optional` → Regular core steps (always included)
- `s.disable_adaptation` → Conditional steps marked to skip filtering (always included)
- `s.optional and not s.disable_adaptation` → Optional steps subject to semantic filtering

### Step 3: Update Picnic Table Workflow

**File**: `server/router/application/workflows/custom/picnic_table.yaml`

Add `disable_adaptation: true` to **20 conditional leg stretching steps**:

**Steps to modify**:
- Steps 15-19: Left leg stretching (condition: `leg_angle_left > 0.5 or leg_angle_left < -0.5`)
- Steps 22-26: Right leg stretching (condition: `leg_angle_right > 0.5 or leg_angle_right < -0.5`)
- Steps 29-33: Left leg back stretching (condition: `leg_angle_left > 0.5 or leg_angle_left < -0.5`)
- Steps 36-40: Right leg back stretching (condition: `leg_angle_right > 0.5 or leg_angle_right < -0.5`)

**Example** (Step 15, before):
```yaml
# Stretch leg top to reach table (automatic calculation)
# OPTIONAL: Only needed for X-shaped crossed legs with high angles (>0.5 rad)
- tool: system_set_mode
  params:
    mode: EDIT
    object_name: "Leg_FL"
  description: "Enter edit mode to stretch leg top"
  condition: "leg_angle_left > 0.5 or leg_angle_left < -0.5"
  optional: true
  tags: ["x-shaped", "crossed-legs", "leg-stretch"]
```

**Example** (Step 15, after):
```yaml
# Stretch leg top to reach table (automatic calculation)
# OPTIONAL: Only needed for X-shaped crossed legs with high angles (>0.5 rad)
- tool: system_set_mode
  params:
    mode: EDIT
    object_name: "Leg_FL"
  description: "Enter edit mode to stretch leg top"
  condition: "leg_angle_left > 0.5 or leg_angle_left < -0.5"
  optional: true
  disable_adaptation: true  # NEW: Skip semantic filtering, condition controls execution
  tags: ["x-shaped", "crossed-legs", "leg-stretch"]
```

**Apply to all 20 conditional steps** (grep: `condition: "leg_angle`)

---

## Testing

### Test Case 1: X-Shaped Legs
**Prompt**: `"stół z nogami w X"`
**Parameters**: `leg_angle_left: 1.0, leg_angle_right: -1.0`

**Expected**:
- WorkflowAdapter includes all 67 steps (core: 22, conditional: 45 via `disable_adaptation`)
- ConditionEvaluator evaluates: `1.0 > 0.5` → True, `-1.0 < -0.5` → True
- Conditional steps execute
- **Result**: 67 tool calls ✅

### Test Case 2: Picnic Table Default
**Prompt**: `"stół piknikowy"`
**Parameters**: `leg_angle_left: 0.32, leg_angle_right: -0.32`

**Expected**:
- WorkflowAdapter includes all 67 steps (core: 22, conditional: 45 via `disable_adaptation`)
- ConditionEvaluator evaluates: `0.32 > 0.5` → False, `-0.32 < -0.5` → False
- Conditional steps skipped by condition
- **Result**: 47 tool calls ✅ (22 core + 25 non-conditional optional)

### Test Case 3: Straight Legs
**Prompt**: `"stół z prostymi nogami"`
**Parameters**: `leg_angle_left: 0, leg_angle_right: 0`

**Expected**:
- WorkflowAdapter includes all 67 steps (core: 22, conditional: 45 via `disable_adaptation`)
- ConditionEvaluator evaluates: `0 > 0.5` → False, `0 < -0.5` → False
- Conditional steps skipped by condition
- **Result**: 22 tool calls ✅

---

## Files to Modify

1. **`server/router/application/workflows/base.py`**
   - Add `disable_adaptation: bool = False` to WorkflowStep dataclass

2. **`server/router/application/engines/workflow_adapter.py`**
   - Update `core_steps` list comprehension (line 139)
   - Update `optional_steps` list comprehension (line 140)

3. **`server/router/application/workflows/custom/picnic_table.yaml`**
   - Add `disable_adaptation: true` to 20 conditional steps (steps 15-19, 22-26, 29-33, 36-40)

---

## Success Criteria

- ✅ X-shaped legs: 67 tool calls (all conditional steps execute)
- ✅ Picnic table: 47 tool calls (conditional steps included but skipped by condition)
- ✅ Straight legs: 22 tool calls (conditional steps included but skipped by condition)
- ✅ Semantic adaptation still works for other optional steps (e.g., bench steps without conditions)
- ✅ Clean separation: `disable_adaptation` for condition-based steps, semantic filtering for tag-based steps
- ✅ Multilingual support: Works with Polish/English prompts (no tag matching dependency)

---

## Related Tasks

- **TASK-055**: Router Interactive Parameter Resolution (parent)
- **TASK-055-FIX-4**: Router Workflow Parameter Passing Bug (previous fix - enables condition evaluation)
- **TASK-041**: Router YAML Workflow Integration (introduced conditional steps)
- **TASK-051**: Confidence-Based Workflow Adaptation (introduced optional step filtering)

---

## Notes

### Why Not Remove `optional: true`?

**Alternative**: Simply remove `optional: true` from conditional steps.

**Why not**:
- Loss of semantic documentation (step is optional feature)
- Tags become meaningless (only optional steps should have tags)
- Less explicit intent (why is this core when it's optional?)

**Why `disable_adaptation` is better**:
- Preserves `optional` semantic meaning for documentation
- Explicit intent: "This is optional but don't filter it semantically"
- Future-proof: Other workflows can use same pattern
- Separation of concerns: semantic filtering vs mathematical conditions

### Adaptation Flow After Fix

**For MEDIUM confidence**:
1. Ensemble matcher sets `requires_adaptation=True`
2. WorkflowAdapter separates:
   - **Core**: `not optional` OR `disable_adaptation=True` → 67 steps
   - **Optional**: `optional=True` AND `disable_adaptation=False` → 0 steps (none in this workflow)
3. All 67 steps passed to registry
4. ConditionEvaluator evaluates conditions on each step
5. Only steps with `condition=True` execute

**Result**: Condition controls execution, not semantic filtering ✅
