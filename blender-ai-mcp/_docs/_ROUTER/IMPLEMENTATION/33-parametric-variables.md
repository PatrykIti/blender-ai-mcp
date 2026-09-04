# 33 - Parametric Variables

## Overview

Parametric variables allow workflow parameters to be modified dynamically based on user prompts. This enables a single workflow to produce different results (e.g., angled vs straight legs) without creating separate workflows.

**Task:** TASK-052
**Status:** ✅ Done
**Date:** 2025-12-07

---

## Interface

No new interfaces were added. The feature extends existing `WorkflowDefinition` and `WorkflowRegistry`.

---

## Implementation

### 1. WorkflowDefinition Extension

```python
# server/router/application/workflows/base.py

@dataclass
class WorkflowDefinition:
    name: str
    description: str
    steps: List[WorkflowStep]
    # ... existing fields ...

    # NEW: TASK-052
    defaults: Optional[Dict[str, Any]] = None      # Default variable values
    modifiers: Optional[Dict[str, Dict[str, Any]]] = None  # Keyword → overrides
```

### 2. Extract Modifiers Function

```python
# server/router/application/engines/workflow_expansion_engine.py

def extract_modifiers(
    prompt: str, workflow_modifiers: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """Extract variable overrides from user prompt based on workflow modifiers.

    Args:
        prompt: User prompt to scan for keywords.
        workflow_modifiers: Dictionary mapping keywords to variable overrides.

    Returns:
        Dictionary of variable overrides found in the prompt.
    """
    overrides: Dict[str, Any] = {}
    prompt_lower = prompt.lower()

    for keyword, values in workflow_modifiers.items():
        if keyword.lower() in prompt_lower:
            overrides.update(values)
            logger.debug(f"Modifier matched: '{keyword}' → {values}")

    return overrides
```

### 3. Substitute Variables Function

```python
# server/router/application/engines/workflow_expansion_engine.py

def substitute_variables(
    params: Dict[str, Any], variables: Dict[str, Any]
) -> Dict[str, Any]:
    """Replace $variable placeholders with actual values.

    Handles both top-level string values and values within lists.
    Variables are referenced with $ prefix (e.g., "$leg_angle").

    Args:
        params: Parameters dictionary with potential $variable references.
        variables: Dictionary of variable names to values.

    Returns:
        New parameters dictionary with variables substituted.
    """
    result: Dict[str, Any] = {}

    for key, value in params.items():
        if isinstance(value, str) and value.startswith("$"):
            var_name = value[1:]  # Remove $
            if var_name in variables:
                result[key] = variables[var_name]
            else:
                # Keep as-is if variable not found (might be $CALCULATE etc.)
                result[key] = value
        elif isinstance(value, list):
            result[key] = _substitute_list(value, variables)
        elif isinstance(value, dict):
            result[key] = substitute_variables(value, variables)
        else:
            result[key] = value

    return result


def _substitute_list(lst: List[Any], variables: Dict[str, Any]) -> List[Any]:
    """Substitute variables in list elements."""
    result = []
    for item in lst:
        if isinstance(item, str) and item.startswith("$"):
            var_name = item[1:]
            if var_name in variables:
                result.append(variables[var_name])
            else:
                result.append(item)
        elif isinstance(item, list):
            result.append(_substitute_list(item, variables))
        elif isinstance(item, dict):
            result.append(substitute_variables(item, variables))
        else:
            result.append(item)
    return result
```

### 4. Registry Integration

```python
# server/router/application/workflows/registry.py

def expand_workflow(
    self,
    workflow_name: str,
    params: Optional[Dict[str, Any]] = None,
    user_prompt: Optional[str] = None,  # NEW: TASK-052
) -> List[CorrectedToolCall]:
    """Expand workflow with optional modifier extraction."""

    definition = self.get_definition(workflow_name)
    if not definition:
        return []

    # Build variables: defaults → modifiers → explicit params
    variables = dict(definition.defaults or {})

    if user_prompt and definition.modifiers:
        overrides = extract_modifiers(user_prompt, definition.modifiers)
        variables.update(overrides)

    if params:
        variables.update(params)

    # Expand steps with variable substitution
    calls = []
    for step in definition.steps:
        resolved_params = substitute_variables(step.params, variables)
        calls.append(CorrectedToolCall(
            tool_name=step.tool,
            params=resolved_params,
        ))

    return calls
```

---

## YAML Schema

### Workflow with Parametric Variables

```yaml
name: picnic_table_workflow
description: Picnic table with configurable legs

# Default variable values
defaults:
  leg_angle_left: 0.32      # radians (~18° for A-frame)
  leg_angle_right: -0.32

# Keyword → variable mappings
modifiers:
  # English
  "straight legs":
    leg_angle_left: 0
    leg_angle_right: 0
  "vertical legs":
    leg_angle_left: 0
    leg_angle_right: 0

  # Polish
  "proste nogi":
    leg_angle_left: 0
    leg_angle_right: 0

steps:
  - tool: modeling_transform_object
    params:
      name: "Leg_FL"
      rotation: [0, "$leg_angle_left", 0]  # Uses variable
```

---

## Variable Resolution Order

1. **defaults** - Workflow-defined default values
2. **modifiers** - Overrides from user prompt keywords
3. **params** - Explicit parameters passed to expand_workflow()

Later values override earlier ones.

---

## Configuration

No new configuration options. Uses existing `RouterConfig`.

---

## Tests

### Location
`tests/unit/router/application/test_variable_substitution.py`

### Test Classes

| Class | Tests | Description |
|-------|-------|-------------|
| `TestExtractModifiers` | 9 | Keyword extraction from prompts |
| `TestSubstituteVariables` | 12 | Variable substitution in params |
| `TestSubstituteList` | 3 | List element substitution |
| `TestWorkflowDefinitionWithModifiers` | 6 | Definition with defaults/modifiers |
| `TestRegistryModifierIntegration` | 4 | Full workflow expansion |
| `TestPicnicTableWorkflow` | 3 | Real workflow tests |

### Running Tests

```bash
PYTHONPATH=. poetry run pytest tests/unit/router/application/test_variable_substitution.py -v
```

---

## Usage

### Programmatic

```python
from server.router.application.workflows.registry import get_workflow_registry

registry = get_workflow_registry()

# Without user prompt - uses defaults
calls = registry.expand_workflow("picnic_table_workflow", {})
# → leg angles are 0.32 (A-frame)

# With user prompt - modifier extraction
calls = registry.expand_workflow(
    "picnic_table_workflow",
    {},
    user_prompt="table with straight legs"
)
# → leg angles are 0 (vertical)

# With explicit params - overrides everything
calls = registry.expand_workflow(
    "picnic_table_workflow",
    {"leg_angle_left": 0.5}
)
# → leg_angle_left is 0.5
```

### Via Router

The router automatically passes user prompt to workflow expansion:

```python
router.process_llm_tool_call(
    "router_set_goal",
    {"goal": "picnic table with straight legs"}
)
# → Router finds workflow, extracts modifiers, expands with straight legs
```

---

## Limitations

1. **Keyword matching is substring-based**
   - "straight" matches "straightforward"
   - Use specific phrases to avoid false matches

2. **No regex support**
   - Keywords are plain strings only
   - For complex patterns, use LaBSE sample_prompts (TASK-046)

3. **No arithmetic in modifiers**
   - Modifiers set literal values only
   - Use `$CALCULATE` in step params for computations

---

## See Also

- [32-workflow-adapter.md](./32-workflow-adapter.md) - Confidence-based adaptation (TASK-051)
- [25-expression-evaluator.md](./25-expression-evaluator.md) - $CALCULATE expressions
- [yaml-workflow-guide.md](../WORKFLOWS/yaml-workflow-guide.md) - Complete YAML reference
- [expression-reference.md](../WORKFLOWS/expression-reference.md) - Expression syntax
