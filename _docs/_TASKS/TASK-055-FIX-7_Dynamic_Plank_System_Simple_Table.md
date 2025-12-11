# TASK-055-FIX-7: Dynamic Plank System + Parameter Renaming for simple_table.yaml

**Status**: 🚧 In Progress
**Priority**: Medium
**Estimated Effort**: 3-4 hours
**Dependencies**: TASK-055-FIX-6 (Flexible YAML Parameter Loading), TASK-056 (Workflow System Enhancements)
**Updated**: 2025-12-11 (Revised to use TASK-056 computed parameters)

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

- **Parameters section**: ~40 lines
- **Planks section**: ~150 lines (15 × 10 lines per plank)
- **Legs section**: 8 lines (4 legs × 2 parameters)
- **Total**: ~200 lines

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
