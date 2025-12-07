# TASK-052: Parametric Workflow Variables

**Status:** 🔴 Planned
**Priority:** High
**Estimated Effort:** Small (1-2 days)
**Dependencies:** TASK-051 (Confidence-Based Workflow Adaptation)

---

## Problem Statement

The current workflow system (TASK-051) can **skip or include** steps but **cannot modify parameters**.

**Example:**
```
User: "rectangular table with 4 straight legs"
Expected: Table with vertical legs (rotation = [0, 0, 0])
Actual: Table with A-frame angled legs (rotation = [0, 0.32, 0])
```

Static parameters in workflow:
```yaml
- tool: modeling_transform_object
  params:
    name: "Leg_FL"
    rotation: [0, 0.32, 0]  # Fixed - CANNOT be changed
```

---

## Solution: $variable Substitution + Keyword Modifiers

### Concept

Prosta rozbudowa istniejącego systemu `$CALCULATE` / `$AUTO_*`:

1. **Workflow YAML** definiuje zmienne z wartościami domyślnymi
2. **Keyword modifiers** mapują frazy użytkownika na wartości zmiennych
3. **Substitution** podmienia `$variable` na wartość podczas expansion

### Architecture

```
User: "table with straight legs"
              │
              ▼
┌─────────────────────────────────────┐
│  Keyword Modifier Matching          │
│  "straight legs" → leg_angle = 0    │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│  Workflow Expansion (existing)      │
│  + Variable Substitution            │
│                                     │
│  rotation: [0, "$leg_angle", 0]     │
│           ↓                         │
│  rotation: [0, 0, 0]                │
└─────────────────────────────────────┘
              │
              ▼
       Execute workflow
```

---

## Implementation

### 1. YAML Schema Extension

```yaml
name: picnic_table_workflow
description: Picnic table with configurable legs

# NEW: Default variable values
defaults:
  leg_angle: 0.32      # radians (~18° for A-frame)
  leg_angle_neg: -0.32 # negative for opposite side
  table_height: 0.254

# NEW: Keyword → variable mappings
modifiers:
  "straight legs":
    leg_angle: 0
    leg_angle_neg: 0
  "proste nogi":
    leg_angle: 0
    leg_angle_neg: 0
  "a-frame":
    leg_angle: 0.32
    leg_angle_neg: -0.32
  "skośne nogi":
    leg_angle: 0.32
    leg_angle_neg: -0.32
  "coffee table":
    table_height: 0.15
  "stolik kawowy":
    table_height: 0.15

steps:
  # Legs use $variable syntax
  - tool: modeling_transform_object
    params:
      name: "Leg_FL"
      rotation: [0, "$leg_angle", 0]  # Will be substituted!

  - tool: modeling_transform_object
    params:
      name: "Leg_FR"
      rotation: [0, "$leg_angle_neg", 0]
```

### 2. Modifier Extraction (simple function)

```python
def extract_modifiers(prompt: str, workflow_modifiers: Dict) -> Dict[str, Any]:
    """Extract variable overrides from user prompt."""
    overrides = {}
    prompt_lower = prompt.lower()

    for keyword, values in workflow_modifiers.items():
        if keyword.lower() in prompt_lower:
            overrides.update(values)

    return overrides
```

### 3. Variable Substitution (extend existing)

Już mamy `ExpressionEvaluator` dla `$CALCULATE`. Wystarczy dodać:

```python
def substitute_variables(params: Dict, variables: Dict) -> Dict:
    """Replace $variable with actual values."""
    result = {}
    for key, value in params.items():
        if isinstance(value, str) and value.startswith("$"):
            var_name = value[1:]  # Remove $
            if var_name in variables:
                result[key] = variables[var_name]
            else:
                result[key] = value  # Keep as-is if not found
        elif isinstance(value, list):
            result[key] = [
                variables.get(v[1:], v) if isinstance(v, str) and v.startswith("$") else v
                for v in value
            ]
        else:
            result[key] = value
    return result
```

### 4. Integration Flow

```python
# In WorkflowExpansionEngine.expand()

def expand(self, workflow: WorkflowDefinition, user_prompt: str) -> List[ToolCall]:
    # 1. Get defaults
    variables = dict(workflow.defaults or {})

    # 2. Apply modifiers from prompt
    if workflow.modifiers:
        overrides = extract_modifiers(user_prompt, workflow.modifiers)
        variables.update(overrides)

    # 3. Expand steps with variable substitution
    expanded_steps = []
    for step in workflow.steps:
        params = substitute_variables(step.params, variables)
        expanded_steps.append(ToolCall(step.tool, params))

    return expanded_steps
```

---

## Use Cases

### Case 1: Straight vs Angled Legs

```
User: "table with straight legs"

defaults: {leg_angle: 0.32}
modifiers match: "straight legs" → {leg_angle: 0}
variables: {leg_angle: 0}

Step params: rotation: [0, "$leg_angle", 0]
Result:      rotation: [0, 0, 0]  ✓
```

### Case 2: Coffee Table Height

```
User: "low coffee table"

defaults: {table_height: 0.254}
modifiers match: "coffee table" → {table_height: 0.15}
variables: {table_height: 0.15}

Step params: location: [0, 0, "$table_height"]
Result:      location: [0, 0, 0.15]  ✓
```

### Case 3: Polish Language

```
User: "stół z prostymi nogami"

modifiers match: "proste nogi" → {leg_angle: 0}
Result: straight legs  ✓
```

---

## Files to Modify

### Modified Files
| File | Changes |
|------|---------|
| `server/router/application/workflows/base.py` | Add `defaults`, `modifiers` to WorkflowDefinition |
| `server/router/infrastructure/workflow_loader.py` | Parse `defaults`, `modifiers` from YAML |
| `server/router/application/engines/workflow_expansion_engine.py` | Add `extract_modifiers()`, `substitute_variables()` |
| `server/router/application/workflows/custom/picnic_table.yaml` | Add defaults + modifiers + $variables |

### New Files
| File | Purpose |
|------|---------|
| `tests/unit/router/application/test_variable_substitution.py` | Unit tests |

---

## Example: Updated picnic_table.yaml

```yaml
name: picnic_table_workflow
description: Picnic table with A-frame legs and optional benches

defaults:
  # Leg configuration
  leg_angle_left: 0.32     # +18° (top leans right)
  leg_angle_right: -0.32   # -18° (top leans left)

  # Heights
  table_height: 0.254
  bench_height: -0.081

modifiers:
  # English
  "straight legs":
    leg_angle_left: 0
    leg_angle_right: 0
  "vertical legs":
    leg_angle_left: 0
    leg_angle_right: 0
  "a-frame":
    leg_angle_left: 0.32
    leg_angle_right: -0.32
  "angled legs":
    leg_angle_left: 0.32
    leg_angle_right: -0.32

  # Polish
  "proste nogi":
    leg_angle_left: 0
    leg_angle_right: 0
  "skośne nogi":
    leg_angle_left: 0.32
    leg_angle_right: -0.32

steps:
  # ... table top steps unchanged ...

  # Front-left leg - uses variable
  - tool: modeling_transform_object
    params:
      name: "Leg_FL"
      scale: [0.024, 0.024, 0.458]
      location: [-0.356, -0.636, -0.190]
      rotation: [0, "$leg_angle_left", 0]
    description: "Front-left leg"

  # Front-right leg - uses variable
  - tool: modeling_transform_object
    params:
      name: "Leg_FR"
      scale: [0.024, 0.024, 0.458]
      location: [0.370, -0.636, -0.190]
      rotation: [0, "$leg_angle_right", 0]
    description: "Front-right leg"

  # ... etc ...
```

---

## Success Criteria

1. **Functional:**
   - "straight legs" → rotation = 0 dla wszystkich nóg
   - "proste nogi" → rotation = 0 (Polish support)
   - Default (no modifier) → A-frame legs (0.32 rad)

2. **Performance:**
   - < 1ms additional processing time
   - No external calls

3. **Quality:**
   - Unit tests for `extract_modifiers()` and `substitute_variables()`
   - E2E test: "table with straight legs" creates correct geometry

---

## Comparison: Original vs Simplified

| Aspect | Original TASK-052 | Simplified |
|--------|-------------------|------------|
| **Effort** | 2-3 weeks | 1-2 days |
| **New classes** | 3 (Engine, Extractor, ParamMapping) | 0 (just functions) |
| **Lines of code** | ~500 | ~50 |
| **YAML complexity** | `param_mapping` with `affects`, `step_pattern`, `param_path` | Simple `defaults` + `modifiers` |
| **Capability** | Post-hoc param modification | Explicit $variable substitution |

The simplified approach is sufficient for the current use cases and can be extended later if needed.

---

## Documentation Update Checklist

After completing this task, update the following documentation files:

### Required Updates

| # | File | What to Update |
|---|------|----------------|
| 1 | `_docs/_TASKS/README.md` | Move TASK-052 to Done section, update statistics |
| 2 | `_docs/_CHANGELOG/98-YYYY-MM-DD-parametric-variables.md` | Create new changelog entry |
| 3 | `_docs/_CHANGELOG/README.md` | Add entry to index table |
| 4 | `_docs/_TESTS/README.md` | Update test count if significant tests added |
| 5 | `_docs/_ROUTER/IMPLEMENTATION/33-parametric-variables.md` | Create implementation doc |
| 6 | `_docs/_ROUTER/IMPLEMENTATION/README.md` | Add entry for 33-parametric-variables |
| 7 | `_docs/_ROUTER/WORKFLOWS/creating-workflows-tutorial.md` | Add `defaults` + `modifiers` + `$variable` syntax |
| 8 | `_docs/_ROUTER/WORKFLOWS/README.md` | Update schema reference, add modifiers section |
| 9 | `_docs/_ROUTER/WORKFLOWS/yaml-workflow-guide.md` | Add parametric variables section |
| 10 | `_docs/_ROUTER/WORKFLOWS/expression-reference.md` | Add `$variable` syntax reference |

### Optional Updates

| File | Condition |
|------|-----------|
| `_docs/_ROUTER/README.md` | If router capabilities summary needs update |
| `README.md` | If main roadmap needs update |
