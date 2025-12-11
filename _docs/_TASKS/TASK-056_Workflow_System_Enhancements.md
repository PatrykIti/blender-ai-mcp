# TASK-056: Workflow System Enhancements

**Status**: 📋 Planned
**Priority**: High
**Estimated Effort**: 8-12 hours
**Dependencies**: TASK-055-FIX-6 (Flexible YAML Parameter Loading)

---

## Overview

Enhance the workflow system with advanced features identified through codebase analysis. This task adds critical missing functionality to expression evaluation, condition evaluation, parameter validation, and step execution control.

---

## Problem Statement

Current workflow system has several limitations that prevent complex parametric workflows:

1. **Limited Math Functions**: Missing trigonometric, logarithmic, and advanced functions
2. **Weak Boolean Logic**: No parentheses support for complex conditions
3. **No Parameter Validation**: Missing enum constraints, pattern matching, dependencies
4. **Limited Step Control**: No timeout, retry, dependencies, or grouping
5. **No Computed Parameters**: Cannot derive parameters from others

### Impact

These limitations prevent workflows from:
- Using advanced mathematical formulas (tan, atan2, log, exp)
- Expressing complex branching logic with proper precedence
- Validating discrete parameter choices (enums)
- Creating robust workflows with error handling (retries, timeouts)
- Defining parameter relationships (derived values, dependencies)

---

## Sub-Tasks

### TASK-056-1: Extended Expression Evaluator

**Priority**: High
**Estimated Effort**: 2 hours

#### Objective

Add missing mathematical functions to expression evaluator whitelist.

#### Implementation

**File**: `server/router/application/evaluator/expression_evaluator.py`

**Current Whitelist** (lines 44-54):
```python
FUNCTIONS = {
    "abs": abs,
    "min": min,
    "max": max,
    "round": round,
    "floor": math.floor,
    "ceil": math.ceil,
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
}
```

**Add New Functions**:
```python
FUNCTIONS = {
    # Existing
    "abs": abs,
    "min": min,
    "max": max,
    "round": round,
    "floor": math.floor,
    "ceil": math.ceil,
    "sqrt": math.sqrt,

    # Trigonometric (existing)
    "sin": math.sin,
    "cos": math.cos,

    # Trigonometric (NEW)
    "tan": math.tan,           # Tangent
    "asin": math.asin,         # Arc sine
    "acos": math.acos,         # Arc cosine
    "atan": math.atan,         # Arc tangent
    "atan2": math.atan2,       # Two-argument arc tangent
    "degrees": math.degrees,   # Radians to degrees
    "radians": math.radians,   # Degrees to radians

    # Logarithmic (NEW)
    "log": math.log,           # Natural logarithm
    "log10": math.log10,       # Base-10 logarithm
    "exp": math.exp,           # e^x

    # Advanced (NEW)
    "pow": pow,                # Alternative to ** operator
    "hypot": math.hypot,       # Hypotenuse (sqrt(x^2 + y^2))
    "trunc": math.trunc,       # Integer truncation
}
```

#### Use Cases

**Example 1: Calculate angle from dimensions**
```yaml
rotation: ["$CALCULATE(atan2(height, width))", 0, 0]
```

**Example 2: Logarithmic scaling**
```yaml
scale: ["$CALCULATE(log10(object_count + 1))", 1, 1]
```

**Example 3: Exponential decay**
```yaml
alpha: "$CALCULATE(exp(-distance / falloff_radius))"
```

#### Testing

- Unit tests for each new function
- Integration test with workflow YAML
- Edge case handling (division by zero, domain errors)

#### Acceptance Criteria

- [ ] All 13 new functions added to whitelist
- [ ] Unit tests pass for each function
- [ ] Documentation updated with function reference
- [ ] Example workflows demonstrate new capabilities

---

### TASK-056-2: Parentheses Support in Condition Evaluator

**Priority**: High
**Estimated Effort**: 3 hours

#### Objective

Enable complex boolean expressions with proper precedence using parentheses.

#### Current Limitation

**File**: `server/router/application/evaluator/condition_evaluator.py` (lines 151-162)

```python
# Handle "X and Y" - only splits on FIRST occurrence!
if " and " in condition:
    parts = condition.split(" and ", 1)
    left = self._evaluate_expression(parts[0].strip())
    right = self._evaluate_expression(parts[1].strip())
    return left and right
```

**Problem**: Cannot parse `(A and B) or (C and D)` or `A and B and C`

#### Implementation Approach

**Option A: Recursive Descent Parser** (Recommended)

```python
class ConditionEvaluator:
    def _parse_or_expression(self, condition: str) -> bool:
        """Parse OR expressions with lower precedence."""
        # Split on 'or' (lower precedence)
        parts = self._split_top_level(condition, " or ")
        if len(parts) > 1:
            return any(self._parse_and_expression(p) for p in parts)
        return self._parse_and_expression(condition)

    def _parse_and_expression(self, condition: str) -> bool:
        """Parse AND expressions with higher precedence."""
        # Split on 'and' (higher precedence)
        parts = self._split_top_level(condition, " and ")
        if len(parts) > 1:
            return all(self._parse_not_expression(p) for p in parts)
        return self._parse_not_expression(condition)

    def _parse_not_expression(self, condition: str) -> bool:
        """Parse NOT expressions and parentheses."""
        condition = condition.strip()

        # Handle 'not' prefix
        if condition.startswith("not "):
            return not self._parse_primary(condition[4:].strip())

        return self._parse_primary(condition)

    def _parse_primary(self, condition: str) -> bool:
        """Parse primary expressions (parentheses or comparison)."""
        condition = condition.strip()

        # Handle parentheses
        if condition.startswith("(") and condition.endswith(")"):
            return self._parse_or_expression(condition[1:-1])

        # Handle comparison operators
        return self._evaluate_comparison(condition)

    def _split_top_level(self, text: str, delimiter: str) -> List[str]:
        """Split on delimiter, respecting parentheses nesting."""
        parts = []
        current = []
        depth = 0

        i = 0
        while i < len(text):
            if text[i] == '(':
                depth += 1
                current.append(text[i])
            elif text[i] == ')':
                depth -= 1
                current.append(text[i])
            elif depth == 0 and text[i:i+len(delimiter)] == delimiter:
                parts.append(''.join(current).strip())
                current = []
                i += len(delimiter) - 1
            else:
                current.append(text[i])
            i += 1

        if current:
            parts.append(''.join(current).strip())

        return parts if len(parts) > 1 else [text]
```

#### Use Cases

**Example 1: Complex leg angle logic**
```yaml
condition: "(leg_angle_left > 0.5 and has_selection) or (object_count >= 3 and current_mode == 'EDIT')"
```

**Example 2: Nested conditions**
```yaml
condition: "not (leg_style == 'straight' or (leg_angle < 0.1 and leg_angle > -0.1))"
```

**Example 3: Multiple AND/OR**
```yaml
condition: "width > 1.0 and length > 1.0 and height > 0.5 or is_tall"
# Evaluates as: ((width > 1.0 and length > 1.0) and height > 0.5) or is_tall
```

#### Testing

- Unit tests for operator precedence
- Parentheses nesting validation
- Complex boolean expressions
- Edge cases (unbalanced parentheses, empty expressions)

#### Acceptance Criteria

- [ ] Parentheses support implemented
- [ ] Operator precedence correct: `not` > `and` > `or`
- [ ] Nested parentheses work up to depth 5
- [ ] Error handling for malformed expressions
- [ ] All existing condition tests still pass

---

### TASK-056-3: Enum Parameter Validation

**Priority**: High
**Estimated Effort**: 2 hours

#### Objective

Add enum constraint validation for discrete parameter choices.

#### Implementation

**File**: `server/router/domain/entities/parameter.py`

**Update ParameterSchema**:
```python
@dataclass
class ParameterSchema:
    name: str
    type: str
    range: Optional[Tuple[float, float]] = None
    default: Any = None
    description: str = ""
    semantic_hints: List[str] = field(default_factory=list)
    group: Optional[str] = None

    # NEW: Enum constraint
    enum: Optional[List[Any]] = None

    def validate_value(self, value: Any) -> bool:
        """Validate value against schema constraints.

        Returns:
            True if value is valid, False otherwise.
        """
        # Type validation
        if self.type == "float":
            if not isinstance(value, (int, float)):
                return False
        elif self.type == "int":
            if not isinstance(value, int) or isinstance(value, bool):
                return False
        elif self.type == "bool":
            if not isinstance(value, bool):
                return False
        elif self.type == "string":
            if not isinstance(value, str):
                return False

        # Enum validation (NEW)
        if self.enum is not None and value not in self.enum:
            return False

        # Range validation
        if self.range is not None and self.type in ("float", "int"):
            min_val, max_val = self.range
            if not (min_val <= value <= max_val):
                return False

        return True
```

**Note**: Current code has `validate_value()` method (lines 59-88). We extend it to add enum validation.

#### YAML Syntax

```yaml
parameters:
  leg_style:
    type: string
    enum: ["straight", "angled", "crossed", "A-frame"]
    default: "straight"
    description: Style of table legs
    semantic_hints:
      - style
      - legs
      - type
    group: leg_config

  material_type:
    type: string
    enum: ["wood", "metal", "plastic", "glass"]
    default: "wood"
    description: Material for table construction
    semantic_hints:
      - material
      - texture
    group: materials
```

#### Use Cases

**Example 1: Furniture style selection**
```yaml
parameters:
  table_style:
    type: string
    enum: ["modern", "rustic", "industrial", "traditional"]
    default: "modern"
```

**Example 2: Quality presets**
```yaml
parameters:
  detail_level:
    type: string
    enum: ["low", "medium", "high", "ultra"]
    default: "medium"
    description: Mesh detail level (affects polygon count)
```

#### Testing

- Enum validation with valid values
- Rejection of invalid values
- Case-sensitive matching
- Empty enum list handling

#### Acceptance Criteria

- [ ] `enum` field added to ParameterSchema
- [ ] `validate_value()` method enforces enum constraints
- [ ] Workflow loader parses enum from YAML
- [ ] Documentation updated with examples

---

### TASK-056-4: Step Dependencies and Execution Control

**Priority**: Medium
**Estimated Effort**: 3 hours

#### Objective

Add step dependency resolution, timeout, and retry mechanisms.

#### Implementation

**File**: `server/router/application/workflows/base.py`

**Update WorkflowStep**:
```python
@dataclass
class WorkflowStep:
    tool: str
    params: Dict[str, Any]
    description: Optional[str] = None
    condition: Optional[str] = None
    optional: bool = False
    disable_adaptation: bool = False
    tags: List[str] = field(default_factory=list)

    # NEW: Execution control (TASK-056-4)
    id: Optional[str] = None                    # Unique step identifier
    depends_on: List[str] = field(default_factory=list)  # Step IDs this depends on
    timeout: Optional[float] = None             # Timeout in seconds
    max_retries: int = 0                        # Number of retry attempts
    retry_delay: float = 1.0                    # Delay between retries (seconds)
    on_failure: Optional[str] = None            # "skip", "abort", "continue"
    priority: int = 0                           # Execution priority (higher = earlier)
```

**File**: `server/router/infrastructure/workflow_loader.py`

**Add Dependency Resolution**:
```python
class WorkflowLoader:
    def _resolve_dependencies(self, steps: List[WorkflowStep]) -> List[WorkflowStep]:
        """Topologically sort steps based on dependencies."""
        step_map = {step.id: step for step in steps if step.id}
        sorted_steps = []
        visited = set()

        def visit(step_id: str):
            if step_id in visited:
                return

            step = step_map.get(step_id)
            if not step:
                raise ValueError(f"Dependency not found: {step_id}")

            # Visit dependencies first
            for dep in step.depends_on:
                visit(dep)

            visited.add(step_id)
            sorted_steps.append(step)

        # Visit all steps
        for step in steps:
            if step.id:
                visit(step.id)
            else:
                # Steps without ID go at the end
                sorted_steps.append(step)

        return sorted_steps
```

#### YAML Syntax

```yaml
steps:
  - id: "create_table"
    tool: modeling_create_primitive
    params:
      primitive_type: CUBE
      name: "Table"
    description: Create table base
    timeout: 5.0
    max_retries: 2

  - id: "scale_table"
    tool: modeling_transform_object
    depends_on: ["create_table"]
    params:
      name: "Table"
      scale: [1, 2, 0.1]
    description: Scale table to correct proportions
    on_failure: "abort"

  - id: "add_legs"
    tool: modeling_create_primitive
    depends_on: ["scale_table"]
    params:
      primitive_type: CUBE
      name: "Leg_1"
    priority: 10
    max_retries: 1
    retry_delay: 0.5
```

#### Use Cases

**Example 1: Ensure creation before transformation**
```yaml
steps:
  - id: "create"
    tool: modeling_create_primitive
    params: {primitive_type: CUBE}

  - id: "transform"
    depends_on: ["create"]
    tool: modeling_transform_object
    params: {scale: [1, 2, 1]}
```

**Example 2: Retry on failure**
```yaml
steps:
  - tool: import_fbx
    params: {filepath: "/path/to/model.fbx"}
    max_retries: 3
    retry_delay: 2.0
    timeout: 30.0
    on_failure: "skip"
```

#### Testing

- Dependency graph construction
- Circular dependency detection
- Timeout enforcement
- Retry mechanism
- Priority-based ordering

#### Acceptance Criteria

- [ ] Step dependency resolution working
- [ ] Circular dependencies detected and rejected
- [ ] Timeout kills long-running steps
- [ ] Retry attempts on failure
- [ ] Priority ordering implemented

---

### TASK-056-5: Computed Parameters

**Priority**: Medium
**Estimated Effort**: 2 hours

#### Objective

Enable parameters derived from other parameters via expressions.

#### Implementation

**File**: `server/router/domain/entities/parameter.py`

**Update ParameterSchema**:
```python
@dataclass
class ParameterSchema:
    name: str
    type: str
    range: Optional[Tuple[float, float]] = None
    default: Any = None
    description: str = ""
    semantic_hints: List[str] = field(default_factory=list)
    group: Optional[str] = None
    enum: Optional[List[Any]] = None

    # NEW: Computed parameter
    computed: Optional[str] = None  # Expression to compute value from other params
    depends_on: List[str] = field(default_factory=list)  # Parameters this depends on
```

**File**: `server/router/application/evaluator/expression_evaluator.py`

**Add Computed Parameter Resolution**:
```python
class ExpressionEvaluator:
    def resolve_computed_parameters(
        self,
        schemas: Dict[str, ParameterSchema],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve all computed parameters in dependency order."""
        resolved = dict(context)

        # Build dependency graph
        graph = {
            name: schema.depends_on
            for name, schema in schemas.items()
            if schema.computed
        }

        # Topological sort
        sorted_params = self._topological_sort(graph)

        # Resolve in order
        for param_name in sorted_params:
            schema = schemas[param_name]
            if schema.computed:
                # Evaluate expression with current context
                value = self.resolve_param_value(
                    f"$CALCULATE({schema.computed})",
                    resolved
                )
                resolved[param_name] = value

        return resolved
```

#### YAML Syntax

```yaml
parameters:
  width:
    type: float
    range: [0.4, 2.0]
    default: 1.0
    description: Table width

  height:
    type: float
    range: [0.4, 1.2]
    default: 0.75
    description: Table height

  aspect_ratio:
    type: float
    computed: "width / height"
    depends_on: ["width", "height"]
    description: Auto-calculated width to height ratio

  diagonal:
    type: float
    computed: "hypot(width, height)"
    depends_on: ["width", "height"]
    description: Diagonal distance across table top
```

#### Use Cases

**Example 1: Derived dimensions**
```yaml
parameters:
  table_width: {type: float, default: 1.2}
  table_length: {type: float, default: 0.8}

  plank_width:
    type: float
    computed: "table_width / ceil(table_width / 0.10)"
    depends_on: ["table_width"]
    description: Actual width of each plank
```

**Example 2: Complex calculations**
```yaml
parameters:
  leg_angle: {type: float, default: 0.32}
  leg_length: {type: float, default: 0.75}

  leg_stretch_x:
    type: float
    computed: "leg_length * sin(leg_angle)"
    depends_on: ["leg_length", "leg_angle"]

  leg_stretch_z:
    type: float
    computed: "leg_length * cos(leg_angle)"
    depends_on: ["leg_length", "leg_angle"]
```

#### Testing

- Computed parameter resolution
- Dependency graph construction
- Circular dependency detection
- Expression evaluation with context

#### Acceptance Criteria

- [ ] `computed` field added to ParameterSchema
- [ ] Dependency resolution works correctly
- [ ] Circular dependencies detected
- [ ] Computed values available in workflow steps
- [ ] Documentation with examples

---

## Testing Strategy

### Unit Tests

- Expression evaluator: Test each new math function
- Condition evaluator: Test parentheses and precedence
- Parameter validation: Test enum constraints
- Dependency resolver: Test graph construction
- Computed parameters: Test evaluation order

### Integration Tests

- Workflow loading with new features
- End-to-end execution with dependencies
- Error handling and retry logic
- Complex boolean conditions in workflows

### E2E Tests

- Create test workflow using all new features
- Verify timeout enforcement
- Test retry mechanism
- Validate computed parameters in real workflow

---

## Documentation Updates

### Files to Update

1. **`_docs/_ROUTER/WORKFLOWS/yaml-workflow-guide.md`**
   - Add expression function reference
   - Document parentheses syntax
   - Show enum parameter examples
   - Explain step dependencies
   - Demonstrate computed parameters

2. **`_docs/_ROUTER/README.md`**
   - Update feature matrix
   - Mark new capabilities as ✅

3. **`README.md`**
   - Add to changelog
   - Update feature list

---

## Migration Guide

### Backward Compatibility

All new features are **opt-in** - existing workflows continue to work without changes:

- New math functions: Only used if referenced in expressions
- Parentheses: Only parsed if present in conditions
- Enum validation: Only enforced if `enum` field present
- Dependencies: Only resolved if `depends_on` specified
- Computed parameters: Only evaluated if `computed` field present

### Recommended Migration

For existing workflows using complex logic:

**Before** (TASK-055):
```yaml
# Complex condition split across multiple steps
- tool: mesh_select
  condition: "leg_angle > 0.5"
  optional: true

- tool: mesh_select
  condition: "leg_angle < -0.5"
  optional: true
```

**After** (TASK-056):
```yaml
# Single step with complex condition
- tool: mesh_select
  condition: "(leg_angle > 0.5) or (leg_angle < -0.5)"
  optional: true
```

---

## Success Metrics

- ✅ 13 new math functions available in expressions
- ✅ Parentheses support enables complex boolean logic
- ✅ Enum validation prevents invalid parameter values
- ✅ Step dependencies ensure correct execution order
- ✅ Computed parameters reduce workflow duplication
- ✅ All existing workflows still work (backward compatible)
- ✅ Performance impact < 10% on workflow loading

---

## Related Tasks

- **TASK-055-FIX-6**: Flexible YAML Parameter Loading (prerequisite)
- **TASK-055-FIX-7**: Dynamic Plank System (uses new features)
- **TASK-052**: Intelligent Parametric Adaptation (enhanced by computed params)
- **TASK-051**: Confidence-Based Workflow Adaptation (uses dependencies)

---

## Notes

- Implement sub-tasks in order (1→2→3→4→5) due to dependencies
- Each sub-task is independently testable
- All features are backward compatible
- Performance monitoring required for dependency resolution
