# TASK-055-FIX-7: Dynamic Plank System + Parameter Renaming for simple_table.yaml

**Status**: 🚧 In Progress (Phase 0 ✅ Done, Phase 1-3 pending)
**Priority**: Medium
**Estimated Effort**: 3-4 hours (Phase 0: 1h ✅ Done, Phase 1-3: 2-3h remaining)
**Dependencies**: TASK-055-FIX-6 (Flexible YAML Parameter Loading), TASK-056 (Workflow System Enhancements)
**Updated**: 2025-12-11 (Phase 0 completed: Computed parameters integrated in WorkflowRegistry)

---

## Overview

This task has **two major components**:

1. **Phase 0: Integrate Computed Parameters** ✅ **DONE** (PREREQUISITE)
   - ✅ Fixed missing integration in `WorkflowRegistry.expand_workflow()` (registry.py:252-282)
   - ✅ Enabled TASK-056-5 computed parameters to work in YAML workflows
   - ✅ Added 3 unit tests (test_registry.py:262-400)
   - ✅ All tests passing (26/26)
   - **Result**: Computed parameters now fully integrated and ready for use

2. **Phase 1-3: Update simple_table.yaml** (MAIN TASK - TODO)
   - Rename parameters to shorter names
   - Add dynamic plank system with computed parameters
   - Use TASK-056 features for clean, performant workflow

---

## Problem Statement

Current `simple_table.yaml` workflow has three limitations:

1. **Verbose parameter names**: `leg_offset_from_beam` and `leg_offset_from_beam_lengthwise` are too long
2. **Fixed plank count**: Always uses 5 planks regardless of table width
3. **Unrealistic scaling**: Wide tables create unrealistically wide planks (e.g., 0.8m width = 0.16m per plank)

### User Requirements

From user feedback:
- ✅ Rename to shorter, technical names: `leg_offset_x` and `leg_offset_y`
- ✅ Dynamic plank count based on table width
- ✅ Maximum plank width: 0.10m (10cm realistic wood plank)
- ✅ **Fractional plank support**: Last plank can be narrower if width doesn't divide evenly

---

## Technical Analysis

### Current Workflow Capabilities (TASK-055-FIX-6 + TASK-056)

**Supported**:
- ✅ Variable substitution: `$table_width`
- ✅ Math expressions: `$CALCULATE(table_width / 5)`
- ✅ Functions: `ceil()`, `floor()`, `sin()`, `cos()`, `abs()`, `min()`, `max()`, `sqrt()`, `tan()`, `atan2()`, `log()`, `exp()`, `hypot()`, `trunc()` (TASK-056-1)
- ✅ **Computed parameters**: Auto-calculated values with dependency resolution (TASK-056-5)
- ✅ **Enum validation**: Discrete parameter constraints (TASK-056-3)
- ✅ Conditional execution: `condition: "leg_angle > 0.5"` with parentheses support (TASK-056-2)
- ✅ Optional steps: `optional: true`, `tags: ["bench"]`
- ✅ Per-step adaptation control: `disable_adaptation: true`

**NOT Supported**:
- ❌ Loops/iteration: No `for`, `while`, or `repeat` constructs
- ❌ Dynamic step generation: Cannot create N steps based on parameter at runtime

### Solution: Conditional Plank System with Computed Parameters

Since we cannot generate dynamic steps, we'll hardcode the **maximum** number of planks (15 for 1.5m max width) and use conditional execution to skip unnecessary planks.

**NEW (TASK-056-5)**: Use **computed parameters** to auto-calculate plank dimensions:

**Calculation Logic**:
```yaml
parameters:
  # User-specified
  table_width:
    type: float
    default: 0.8

  plank_max_width:
    type: float
    default: 0.10

  # Auto-calculated (TASK-056-5)
  plank_count:
    type: int
    computed: "ceil(table_width / plank_max_width)"
    depends_on: ["table_width", "plank_max_width"]

  plank_actual_width:
    type: float
    computed: "table_width / plank_count"
    depends_on: ["table_width", "plank_count"]
```

**Examples**:
| Table Width | `ceil(width/0.10)` | Plank Count | Each Plank Width |
|-------------|-------------------|-------------|------------------|
| 0.80m       | ceil(8.0)         | 8 planks    | 0.10m (exactly)  |
| 0.83m       | ceil(8.3)         | 9 planks    | 0.092m (fragment)|
| 1.20m       | ceil(12.0)        | 12 planks   | 0.10m (exactly)  |
| 0.45m       | ceil(4.5)         | 5 planks    | 0.09m (fragment) |

---

## Implementation Plan

### Phase 0: Integrate Computed Parameters into Workflow Execution ✅ **COMPLETED**

**Status**: ✅ Done (2025-12-11)
- ✅ Implementation completed in `registry.py` (lines 252-282)
- ✅ 3 unit tests added (test_registry.py:262-400)
- ✅ All 26 tests passing
- ✅ Explicit params correctly override computed params
- ✅ Circular dependencies handled gracefully

**Original Problem** (FIXED): `ExpressionEvaluator.resolve_computed_parameters()` was implemented (TASK-056-5) but **NOT called** during workflow execution.

**Why This Phase is Critical**:
Without Phase 0, computed parameters in YAML will be:
- ✅ Loaded from YAML by `WorkflowLoader`
- ✅ Stored in `WorkflowDefinition.parameters`
- ❌ **IGNORED during workflow expansion** (never calculated!)
- ❌ References like `$plank_actual_width` will fail (undefined variable)
- ❌ Conditions like `plank_count >= N` will fail (undefined variable)

**Current Flow** (BROKEN for computed params):
```
WorkflowRegistry.expand_workflow()
  → _build_variables(definition, user_prompt)  # Builds defaults + modifiers
  → all_params = {**variables, **params}
  → _resolve_definition_params(steps, all_params)  # Resolves $variable and $CALCULATE()
  → _steps_to_calls()
```

**Missing Step**: Computed parameters are never resolved! Even though they're loaded from YAML into `definition.parameters`, they're ignored during execution.

---

#### 0.1 Architecture Analysis

**Clean Architecture Layers**:
```
┌─────────────────────────────────────────────────────────────┐
│ DOMAIN LAYER                                                │
│ - ParameterSchema (has computed, depends_on fields)         │
│ - WorkflowDefinition (has parameters: Dict[str, ParameterSchema]) │
├─────────────────────────────────────────────────────────────┤
│ APPLICATION LAYER                                           │
│ - ExpressionEvaluator.resolve_computed_parameters()  ✅     │
│ - WorkflowRegistry.expand_workflow()  ❌ (missing call)    │
├─────────────────────────────────────────────────────────────┤
│ INFRASTRUCTURE LAYER                                        │
│ - WorkflowLoader (loads computed params from YAML)  ✅      │
└─────────────────────────────────────────────────────────────┘
```

**Issue**: Application layer has the method but doesn't use it!

---

#### 0.2 Implementation: Add Computed Parameter Resolution

**File**: `server/router/application/workflows/registry.py`

**Location**: Inside `expand_workflow()` method (line ~250), right after building `all_params`:

```python
def expand_workflow(
    self,
    workflow_name: str,
    params: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
    user_prompt: Optional[str] = None,
) -> List[CorrectedToolCall]:
    """Expand a workflow into tool calls."""
    # ... existing code ...

    # Try custom definition
    definition = self._custom_definitions.get(workflow_name)
    if definition:
        # Build variable context from defaults + modifiers (TASK-052)
        variables = self._build_variables(definition, user_prompt)
        # Merge with params (params override variables)
        all_params = {**variables, **(params or {})}

        # NEW (TASK-055-FIX-7 Phase 0): Resolve computed parameters
        if definition.parameters:
            try:
                # Extract ParameterSchema objects that have computed expressions
                schemas = definition.parameters  # Dict[str, ParameterSchema]

                # Resolve computed parameters in dependency order
                computed_values = self._evaluator.resolve_computed_parameters(
                    schemas, all_params
                )

                # Merge computed values back into all_params
                # Computed params override defaults but NOT explicit params
                all_params = {**all_params, **computed_values}

                logger.debug(
                    f"Resolved {len(computed_values)} computed parameters: "
                    f"{list(computed_values.keys())}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to resolve computed parameters for {workflow_name}: {e}"
                )
                # Continue with non-computed params (degraded mode)

        steps = self._resolve_definition_params(definition.steps, all_params)
        return self._steps_to_calls(steps, workflow_name, workflow_params=all_params)

    return []
```

**Why This Location?**:
1. ✅ After defaults and modifiers are merged
2. ✅ Before step parameter resolution (`$variable` substitution)
3. ✅ Computed params can reference defaults, modifiers, and explicit params
4. ✅ Results available for both conditions and step params

---

#### 0.3 Error Handling Strategy

**Principle**: Degrade gracefully if computed parameter resolution fails.

**Error Cases**:
1. **Circular dependency**: Caught by `_topological_sort()` → raises `ValueError`
2. **Unknown variable in expression**: Caught by `evaluate()` → returns `None`
3. **Invalid expression syntax**: Caught by AST parser → raises `SyntaxError`

**Handling**:
```python
try:
    computed_values = self._evaluator.resolve_computed_parameters(schemas, all_params)
    all_params = {**all_params, **computed_values}
except ValueError as e:
    # Circular dependency or missing required variable
    logger.error(f"Computed parameter dependency error: {e}")
    # Continue without computed params - workflow may fail later with clearer error
except Exception as e:
    # Syntax error, unexpected exception
    logger.error(f"Unexpected error resolving computed parameters: {e}")
    # Continue without computed params
```

**Why Graceful Degradation?**:
- Computed parameters are **opt-in** (backward compatible)
- Workflow without computed params should still work
- Let workflow execution fail naturally if required param is missing
- Easier to debug: clear error message about missing param vs obscure computed param error

---

#### 0.4 Testing Strategy

**Unit Tests** (add to `tests/unit/router/application/workflows/test_registry.py`):

```python
def test_expand_workflow_with_computed_parameters():
    """Test workflow expansion with TASK-056-5 computed parameters."""
    registry = WorkflowRegistry()

    # Create workflow with computed parameters
    definition = WorkflowDefinition(
        name="test_computed",
        description="Test computed params",
        steps=[
            WorkflowStep(
                tool="modeling_create_primitive",
                params={"scale": ["$plank_actual_width", 1, 0.1]}
            )
        ],
        defaults={"table_width": 0.8, "plank_max_width": 0.10},
        parameters={
            "plank_count": ParameterSchema(
                name="plank_count",
                type="int",
                computed="ceil(table_width / plank_max_width)",
                depends_on=["table_width", "plank_max_width"]
            ),
            "plank_actual_width": ParameterSchema(
                name="plank_actual_width",
                type="float",
                computed="table_width / plank_count",
                depends_on=["table_width", "plank_count"]
            )
        }
    )
    registry.register_definition(definition)

    # Expand workflow
    calls = registry.expand_workflow("test_computed")

    # Verify computed params were resolved
    assert len(calls) == 1
    assert calls[0].params["scale"][0] == 0.1  # 0.8 / 8 = 0.1


def test_expand_workflow_computed_params_circular_dependency():
    """Test graceful handling of circular dependency."""
    registry = WorkflowRegistry()

    # Create workflow with circular dependency
    definition = WorkflowDefinition(
        name="test_circular",
        description="Test circular dependency",
        steps=[WorkflowStep(tool="test", params={})],
        parameters={
            "a": ParameterSchema(
                name="a", type="float",
                computed="b + 1", depends_on=["b"]
            ),
            "b": ParameterSchema(
                name="b", type="float",
                computed="a + 1", depends_on=["a"]
            )
        }
    )
    registry.register_definition(definition)

    # Should not crash - degrades gracefully
    calls = registry.expand_workflow("test_circular")
    assert len(calls) == 1  # Workflow still expands


def test_expand_workflow_computed_params_override():
    """Test that explicit params override computed params."""
    registry = WorkflowRegistry()

    definition = WorkflowDefinition(
        name="test_override",
        description="Test computed param override",
        steps=[WorkflowStep(tool="test", params={"count": "$plank_count"})],
        defaults={"width": 0.8},
        parameters={
            "plank_count": ParameterSchema(
                name="plank_count", type="int",
                computed="ceil(width / 0.1)", depends_on=["width"]
            )
        }
    )
    registry.register_definition(definition)

    # Expand with explicit override
    calls = registry.expand_workflow("test_override", params={"plank_count": 10})

    # Explicit param should override computed
    assert calls[0].params["count"] == 10  # Not 8 (computed value)
```

**Integration Test** (manual verification with simple_table.yaml):

```bash
# Test that computed parameters work in real workflow
ROUTER_ENABLED=true LOG_LEVEL=DEBUG poetry run python -c "
from server.router.application.workflows.registry import get_workflow_registry

registry = get_workflow_registry()
registry.load_custom_workflows()

# Expand simple_table with computed params
calls = registry.expand_workflow('simple_table_workflow', params={'table_width': 0.83})

# Check logs for computed param resolution
# Should see: 'Resolved 2 computed parameters: [plank_count, plank_actual_width]'

# Verify plank_count and plank_actual_width are available in steps
print(f'Total calls: {len(calls)}')
"
```

---

#### 0.5 Clean Architecture Compliance

**Layers Involved**:

1. **Domain Layer** (entities):
   - `ParameterSchema` - already has `computed`, `depends_on` fields ✅
   - `WorkflowDefinition` - already has `parameters: Dict[str, ParameterSchema]` ✅

2. **Application Layer** (business logic):
   - `ExpressionEvaluator.resolve_computed_parameters()` - already implemented ✅
   - `WorkflowRegistry.expand_workflow()` - **ADD CALL HERE** ⚠️

3. **Infrastructure Layer** (frameworks):
   - `WorkflowLoader` - already parses computed params from YAML ✅

**Dependency Rule Check**:
```
Application → Domain ✅ (WorkflowRegistry uses ParameterSchema)
Application → Infrastructure ❌ (WorkflowRegistry does NOT depend on WorkflowLoader)
Infrastructure → Domain ✅ (WorkflowLoader creates ParameterSchema)
```

**No violations!** ✅

---

#### 0.6 Acceptance Criteria for Phase 0

- [ ] `WorkflowRegistry.expand_workflow()` calls `resolve_computed_parameters()`
- [ ] Computed parameters resolved in dependency order (topological sort)
- [ ] Resolved values merged into `all_params` before step resolution
- [ ] Explicit params override computed params
- [ ] Graceful degradation on errors (logged, workflow continues)
- [ ] Unit tests added for computed param resolution
- [ ] Unit tests added for circular dependency handling
- [ ] Unit tests added for explicit override behavior
- [ ] Manual test with simple_table.yaml confirms computed params work
- [ ] Debug logs show resolved computed parameters

---

#### 0.7 Files to Modify (Phase 0)

1. **`server/router/application/workflows/registry.py`** (PRIMARY)
   - Add computed parameter resolution in `expand_workflow()` (line ~250)
   - ~15 lines of code

2. **`tests/unit/router/application/workflows/test_registry.py`** (TESTS)
   - Add 3 new test cases (computed params, circular dependency, override)
   - ~100 lines of test code

---

### Phase 1: Parameter Renaming

**File**: `server/router/application/workflows/custom/simple_table.yaml`

#### 1.1 Update `defaults` Section
```yaml
defaults:
  # OLD
  leg_offset_from_beam: 0.05
  leg_offset_from_beam_lengthwise: 0.05

  # NEW
  leg_offset_x: 0.05         # Distance from crossbeam edge in X axis (width)
  leg_offset_y: 0.05         # Distance from crossbeam edge in Y axis (length)
  plank_max_width: 0.10      # NEW: 10cm realistic plank width
```

#### 1.2 Update `parameters` Section
```yaml
leg_offset_x:
  type: float
  range: [0.02, 0.15]
  default: 0.05
  description: Distance of legs from crossbeam edge in X axis (width)
  semantic_hints:
    - offset
    - beam
    - distance
    - stable
    - position
    - width
    - x-axis
  group: leg_dimensions

leg_offset_y:
  type: float
  range: [0.02, 0.15]
  default: 0.05
  description: Distance of legs from crossbeam edge in Y axis (length)
  semantic_hints:
    - offset
    - lengthwise
    - length
    - corner
    - beam
    - distance
    - y-axis
  group: leg_dimensions

plank_max_width:
  type: float
  range: [0.08, 0.20]
  default: 0.10
  description: Maximum width of individual table planks (realistic wood plank size)
  semantic_hints:
    - plank
    - width
    - board
    - wood
    - size
  group: table_dimensions

# NEW (TASK-056-5): Computed parameters
plank_count:
  type: int
  computed: "ceil(table_width / plank_max_width)"
  depends_on: ["table_width", "plank_max_width"]
  description: Number of planks needed (auto-calculated)
  group: table_dimensions

plank_actual_width:
  type: float
  computed: "table_width / plank_count"
  depends_on: ["table_width", "plank_count"]
  description: Actual width of each plank (adapted to fit exactly)
  group: table_dimensions
```

#### 1.3 Update All Leg Position Formulas

Replace in 4 leg transform steps (Leg_FL, Leg_FR, Leg_BL, Leg_BR):
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

**Lines to update**: 237, 252, 267, 282

---

### Phase 2: Dynamic Plank System

#### 2.1 Remove Fixed 5-Plank System

**Delete** lines 123-186 (current 5 fixed planks)

#### 2.2 Add 15 Conditional Planks (with Computed Parameters)

**Position Formula** (for Plank N, where N = 1, 2, 3...15):
```yaml
# BEFORE (TASK-055-FIX-7 original):
X = -table_width / 2 + table_width / ceil(table_width / plank_max_width) / 2 + (N - 1) * (table_width / ceil(table_width / plank_max_width))

# AFTER (with TASK-056-5 computed parameters):
X = -table_width / 2 + plank_actual_width / 2 + (N - 1) * plank_actual_width
```

**Benefits of Computed Parameters**:
- ✅ **Readability**: `$plank_actual_width` vs `$CALCULATE(table_width / ceil(table_width / plank_max_width))`
- ✅ **Performance**: Calculated once, reused 30 times (15 planks × 2 steps)
- ✅ **Maintainability**: Change formula in one place
- ✅ **Type safety**: `plank_count` is int, validated automatically

**Template for Each Plank**:
```yaml
# --- PLANK N ---
- tool: modeling_create_primitive
  params:
    primitive_type: CUBE
    name: "TablePlank_N"
  description: Create table plank N
  condition: "plank_count >= N"  # Uses computed parameter!
  optional: true

- tool: modeling_transform_object
  params:
    name: "TablePlank_N"
    scale:
      - "$plank_actual_width"  # Clean reference to computed param
      - "$table_length"
      - 0.0114
    location:
      - "$CALCULATE(-table_width / 2 + plank_actual_width / 2 + (N - 1) * plank_actual_width)"
      - 0
      - "$CALCULATE(leg_length + 0.0114)"
  description: "Position plank N - conditionally included"
  condition: "plank_count >= N"  # Uses computed parameter!
  optional: true
```

**Special Case - Plank 1** (always included, no condition):
```yaml
# --- PLANK 1 (ALWAYS) ---
- tool: modeling_create_primitive
  params:
    primitive_type: CUBE
    name: "TablePlank_1"
  description: Create table plank 1 (always included)

- tool: modeling_transform_object
  params:
    name: "TablePlank_1"
    scale:
      - "$plank_actual_width"  # Clean!
      - "$table_length"
      - 0.0114
    location:
      - "$CALCULATE(-table_width / 2 + plank_actual_width / 2)"
      - 0
      - "$CALCULATE(leg_length + 0.0114)"
  description: "Position plank 1 (leftmost) - width adapts to plank count"
```

#### 2.3 Plank Numbering Pattern

Create 15 plank pairs (30 steps total):
- **Plank 1**: No condition (always created)
- **Planks 2-15**: Each with `condition: "plank_count >= N"` (uses computed parameter!)

**Maximum Coverage**: 1.5m / 0.10m = 15 planks

**Why Computed Parameters Are Better**:
| Aspect | Before (TASK-055-FIX-7 original) | After (with TASK-056-5) |
|--------|----------------------------------|-------------------------|
| **Condition** | `"ceil(table_width / plank_max_width) >= N"` | `"plank_count >= N"` |
| **Scale** | `"$CALCULATE(table_width / ceil(...))"` | `"$plank_actual_width"` |
| **Performance** | 30× redundant calculations | 1× calculation, 30× reuse |
| **Readability** | Complex nested expression | Clean variable reference |
| **Type Safety** | Expression result (float) | Validated int parameter |

---

### Phase 3: Testing

#### Test Cases

1. **Default table (0.8m width)**
   - Expected: 8 planks × 0.10m each
   - Verify: Plank count = 8, width = 0.10m

2. **Narrow table (0.45m width)**
   - Expected: 5 planks × 0.09m each (fractional)
   - Verify: Plank count = 5, width = 0.09m

3. **Wide table (1.2m width)**
   - Expected: 12 planks × 0.10m each
   - Verify: Plank count = 12, width = 0.10m

4. **Fractional table (0.83m width)**
   - Expected: 9 planks × 0.0922m each (fractional)
   - Verify: Plank count = 9, width ≈ 0.0922m

5. **Maximum table (1.5m width)**
   - Expected: 15 planks × 0.10m each
   - Verify: Plank count = 15, all planks created

#### Manual Testing Commands

```bash
# Clean scene and test workflow
ROUTER_ENABLED=true poetry run python -c "
from server.router.application.router import SupervisorRouter
router = SupervisorRouter()
result = router.set_goal('prosty stół 0.8m szerokości')
print(result)
"
```

---

## Position Calculation Reference

### Formula Derivation

Given:
- `table_width` = total table width (e.g., 0.8m)
- `plank_max_width` = 0.10m (constant)
- `plank_count` = `ceil(table_width / plank_max_width)` (e.g., ceil(8.0) = 8)
- `plank_width` = `table_width / plank_count` (e.g., 0.8 / 8 = 0.10m)
- `plank_index` = 1, 2, 3...N (1-based)

**Plank X position** (centered):
```
X = -table_width/2 + plank_width/2 + (plank_index - 1) * plank_width
```

**Example** (table_width = 0.8m, 8 planks):
| Plank | Index | Formula | X Position |
|-------|-------|---------|------------|
| 1     | 1     | `-0.4 + 0.05 + 0*0.10` | -0.35m |
| 2     | 2     | `-0.4 + 0.05 + 1*0.10` | -0.25m |
| 3     | 3     | `-0.4 + 0.05 + 2*0.10` | -0.15m |
| 4     | 4     | `-0.4 + 0.05 + 3*0.10` | -0.05m |
| 5     | 5     | `-0.4 + 0.05 + 4*0.10` | +0.05m |
| 6     | 6     | `-0.4 + 0.05 + 5*0.10` | +0.15m |
| 7     | 7     | `-0.4 + 0.05 + 6*0.10` | +0.25m |
| 8     | 8     | `-0.4 + 0.05 + 7*0.10` | +0.35m |

---

## Files to Modify

1. **`server/router/application/workflows/custom/simple_table.yaml`**
   - Update defaults section
   - Update parameters section
   - Update 4 leg position formulas
   - Replace 5 fixed planks with 15 conditional planks

---

## Acceptance Criteria

### Phase 0: Computed Parameters Integration ✅ **COMPLETED**
- [x] `WorkflowRegistry.expand_workflow()` calls `resolve_computed_parameters()` (registry.py:264-266)
- [x] Computed parameters resolved in dependency order (topological sort)
- [x] Resolved values merged into `all_params` before step resolution (registry.py:270)
- [x] Explicit params override computed params (registry.py:260-270)
- [x] Graceful degradation on errors (logged, workflow continues) (registry.py:271-282)
- [x] Unit tests added for computed param resolution (test_registry.py:264-318)
- [x] Unit tests added for circular dependency handling (test_registry.py:320-354)
- [x] Unit tests added for explicit override behavior (test_registry.py:356-400)
- [x] All 26 unit tests passing
- [x] Debug logs show resolved computed parameters (registry.py:272-275)

### Phase 1-3: simple_table.yaml Implementation
- [ ] Parameters renamed: `leg_offset_x`, `leg_offset_y`
- [ ] New parameter added: `plank_max_width` (default 0.10)
- [ ] **NEW**: Computed parameters added: `plank_count`, `plank_actual_width` (TASK-056-5)
- [ ] 15 conditional planks implemented with `condition: "plank_count >= N"`
- [ ] Plank scale uses `$plank_actual_width` (computed parameter)
- [ ] Plank width adapts to table width (fractional support)
- [ ] All 4 leg formulas updated
- [ ] Manual tests pass for 0.8m, 0.45m, 1.2m, 0.83m, 1.5m widths
- [ ] Semantic hints updated for new parameter names
- [ ] Verify computed parameters resolve correctly in dependency order

---

## Estimated Changes

### Phase 0: Computed Parameters Integration ✅ **COMPLETED**
- **`registry.py`**: 31 lines added (lines 252-282) ✅
- **`test_registry.py`**: 139 lines added (lines 262-400) ✅
- **Total Phase 0**: 170 lines ✅ (original estimate: 115 lines)

### Phase 1-3: simple_table.yaml
- **Parameters section**: ~60 lines (renamed params + 2 computed params)
- **Planks section**: ~150 lines (15 × 10 lines per plank)
- **Legs section**: 8 lines (4 legs × 2 parameters)
- **Total Phase 1-3**: ~218 lines

### Grand Total
- **Code changes**: ~388 lines (Phase 0: 170 ✅ Done, Phase 1-3: ~218 remaining)
- **Actual effort**:
  - Phase 0: 1 hour ✅ Done (integration + tests)
  - Phase 1-3: 2-3 hours (YAML updates - TODO)
  - **Total**: 3-4 hours (1h completed, 2-3h remaining)

---

## Notes

- This task depends on TASK-055-FIX-6 (conditional execution support) and TASK-056 (computed parameters)
- **TASK-056-5 Integration**: Computed parameters (`plank_count`, `plank_actual_width`) auto-calculated in dependency order
- Fractional plank widths handled automatically: `plank_actual_width = table_width / plank_count`
- Maximum 15 planks covers table widths up to 1.5m (parameter range limit)
- Conditional steps will be skipped automatically by workflow loader if condition is false
- **Performance**: Computed parameters calculated once at workflow start, then reused 30+ times

---

## Related Tasks

- TASK-055-FIX-6: Flexible YAML Parameter Loading (prerequisite)
- TASK-056: Workflow System Enhancements (enables computed parameters)
  - TASK-056-1: Extended math functions (`ceil()` for plank_count)
  - TASK-056-5: Computed parameters (`plank_count`, `plank_actual_width`)
- TASK-052: Intelligent Parametric Adaptation (related concept)
- TASK-051: Confidence-Based Workflow Adaptation (uses conditional execution)

---

---

## Phase 0 Summary: Why Integration is Required

**Discovery**: TASK-056-5 implemented `resolve_computed_parameters()` but never integrated it into workflow execution!

**Impact Without Phase 0**:
```yaml
# This YAML loads successfully...
parameters:
  plank_count:
    type: int
    computed: "ceil(table_width / plank_max_width)"
    depends_on: ["table_width", "plank_max_width"]

steps:
  - tool: modeling_create_primitive
    condition: "plank_count >= 2"  # ❌ ERROR: plank_count undefined!
    params:
      scale: ["$plank_actual_width", 1, 0.1]  # ❌ ERROR: undefined!
```

**Impact With Phase 0**:
```yaml
# Same YAML, but computed params are resolved during expansion!
# plank_count = ceil(0.8 / 0.1) = 8
# plank_actual_width = 0.8 / 8 = 0.1

steps:
  - tool: modeling_create_primitive
    condition: "plank_count >= 2"  # ✅ Evaluates: 8 >= 2 = True
    params:
      scale: ["$plank_actual_width", 1, 0.1]  # ✅ Resolves: [0.1, 1, 0.1]
```

**Clean Architecture Compliance**:
- Domain entities already have fields ✅
- Application layer already has logic ✅
- Missing: **Application layer doesn't call its own logic!** ❌
- Fix: Add 15 lines to `WorkflowRegistry.expand_workflow()` ✅

---

## Benefits Summary: TASK-056 Integration

### Before (Original TASK-055-FIX-7 Plan):
```yaml
# Repeated 30 times across 15 planks:
condition: "ceil(table_width / plank_max_width) >= N"
scale: ["$CALCULATE(table_width / ceil(table_width / plank_max_width))", ...]
location: ["$CALCULATE(-table_width / 2 + table_width / ceil(...) / 2 + (N-1) * table_width / ceil(...))", ...]
```
**Issues**:
- ❌ Verbose and error-prone
- ❌ 30+ redundant `ceil()` calculations
- ❌ Hard to read and maintain
- ❌ Type safety unclear (float vs int)

### After (With TASK-056-5 Computed Parameters):
```yaml
# Defined once in parameters:
plank_count:
  type: int
  computed: "ceil(table_width / plank_max_width)"
  depends_on: ["table_width", "plank_max_width"]

plank_actual_width:
  type: float
  computed: "table_width / plank_count"
  depends_on: ["table_width", "plank_count"]

# Used cleanly in steps:
condition: "plank_count >= N"
scale: ["$plank_actual_width", ...]
location: ["$CALCULATE(-table_width / 2 + plank_actual_width / 2 + (N-1) * plank_actual_width)", ...]
```
**Benefits**:
- ✅ Clean, readable variable references
- ✅ Calculated once, reused 30+ times (performance)
- ✅ Type-safe (int vs float validated)
- ✅ Dependency order automatic (topological sort)
- ✅ Easy to modify formula in one place
- ✅ Self-documenting code
