# TASK-052: Intelligent Parametric Adaptation

**Status:** 🔴 Planned
**Priority:** High
**Estimated Effort:** Large (2-3 weeks)
**Dependencies:** TASK-051 (Confidence-Based Workflow Adaptation)

---

## Problem Statement

### Current Limitation

The current workflow system (TASK-051) can only **skip or include** workflow steps based on confidence level. It **cannot modify parameters** within steps.

**Example:**
```
User: "create a rectangular table with 4 straight legs"
Expected: Table with vertical legs (rotation = [0, 0, 0])
Actual: Table with A-frame angled legs (rotation = [0, 0.32, 0])
```

The workflow defines **static parameters**:
```yaml
- tool: modeling_transform_object
  params:
    name: "Leg_FL"
    rotation: [0, 0.32, 0]  # Fixed 18° angle - CANNOT be changed
```

### Why This Matters

Without parametric adaptation, the router:
1. Cannot create "straight legs" from a workflow with "angled legs"
2. Cannot change table height when user says "low coffee table"
3. Cannot modify dimensions based on "small", "large", "narrow" descriptors
4. Forces users to describe exact workflow matches or accept defaults

---

## Proposed Solution: Option B - Intelligent Parametric Adaptation

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Prompt Analysis                          │
│  "rectangular table with 4 straight legs"                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Intent Extraction                             │
│  - Object: table                                                │
│  - Components: 4 legs                                           │
│  - Modifiers: straight (angle=0), rectangular                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Workflow Matching (existing)                    │
│  Match: picnic_table_workflow (confidence: 0.65 LOW)            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│            NEW: Parametric Adaptation Engine                    │
│                                                                 │
│  1. Extract intent modifiers: "straight" → leg_angle = 0       │
│  2. Find adaptable params in workflow steps                     │
│  3. Generate parameter overrides                                │
│                                                                 │
│  Overrides:                                                     │
│    - Leg_FL.rotation: [0, 0.32, 0] → [0, 0, 0]                 │
│    - Leg_FR.rotation: [0, -0.32, 0] → [0, 0, 0]                │
│    - ...                                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Adapted Workflow Execution                     │
│  Execute workflow with modified parameters                       │
└─────────────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. Intent Modifier Extractor

Extracts semantic modifiers from user prompts:

```python
class IntentModifierExtractor:
    """Extract parametric modifiers from user intent."""

    MODIFIER_PATTERNS = {
        # Leg style
        "straight legs": {"leg_angle": 0},
        "angled legs": {"leg_angle": 0.32},
        "a-frame": {"leg_angle": 0.32},
        "splayed legs": {"leg_angle": 0.25},

        # Size modifiers
        "small": {"scale_factor": 0.5},
        "large": {"scale_factor": 1.5},
        "coffee table": {"height": 0.45},
        "dining table": {"height": 0.75},
        "bar table": {"height": 1.1},

        # Shape modifiers
        "round": {"top_shape": "CYLINDER"},
        "square": {"top_shape": "CUBE", "aspect": 1.0},
        "rectangular": {"top_shape": "CUBE", "aspect": 0.6},
    }

    def extract(self, prompt: str) -> Dict[str, Any]:
        """Extract modifiers from prompt."""
        modifiers = {}
        prompt_lower = prompt.lower()

        for pattern, params in self.MODIFIER_PATTERNS.items():
            if pattern in prompt_lower:
                modifiers.update(params)

        return modifiers
```

#### 2. Workflow Parameter Mapper

Maps workflow step parameters to adaptable concepts:

```yaml
# New YAML field: param_mapping
name: picnic_table_workflow

param_mapping:
  leg_angle:
    description: "Angle of table legs from vertical"
    default: 0.32  # radians (~18°)
    range: [0, 0.5]
    affects:
      - step_pattern: "Leg_*"
        param_path: "rotation[1]"  # Y rotation

  height:
    description: "Table top height from ground"
    default: 0.75  # meters
    range: [0.3, 1.2]
    affects:
      - step_pattern: "TablePlank_*"
        param_path: "location[2]"
      - step_pattern: "Leg_*"
        param_path: "scale[2]"
        transform: "value / 0.916"  # Adjust leg length

  top_width:
    description: "Width of table top"
    default: 0.8
    range: [0.4, 2.0]
    affects:
      - step_pattern: "TablePlank_*"
        param_path: "scale[0]"
        transform: "value / 2"
```

#### 3. Parametric Adaptation Engine

Applies modifiers to workflow steps:

```python
class ParametricAdaptationEngine:
    """Adapts workflow parameters based on intent modifiers."""

    def adapt(
        self,
        workflow: WorkflowDefinition,
        modifiers: Dict[str, Any],
    ) -> List[WorkflowStep]:
        """Adapt workflow steps with parameter overrides."""

        adapted_steps = []
        param_mapping = workflow.param_mapping or {}

        for step in workflow.steps:
            adapted_step = self._adapt_step(step, modifiers, param_mapping)
            adapted_steps.append(adapted_step)

        return adapted_steps

    def _adapt_step(
        self,
        step: WorkflowStep,
        modifiers: Dict[str, Any],
        param_mapping: Dict[str, ParamMappingDef],
    ) -> WorkflowStep:
        """Adapt single step parameters."""

        new_params = dict(step.params)

        for modifier_name, modifier_value in modifiers.items():
            if modifier_name not in param_mapping:
                continue

            mapping = param_mapping[modifier_name]

            for affect in mapping.affects:
                if self._matches_pattern(step, affect.step_pattern):
                    self._apply_param_override(
                        new_params,
                        affect.param_path,
                        modifier_value,
                        affect.transform,
                    )

        return step.copy(params=new_params)
```

### Use Cases

#### Case 1: Straight vs Angled Legs

```
User: "table with straight legs"
Modifier extracted: leg_angle = 0

Original step:
  - tool: modeling_transform_object
    params:
      name: "Leg_FL"
      rotation: [0, 0.32, 0]  # 18° angle

Adapted step:
  - tool: modeling_transform_object
    params:
      name: "Leg_FL"
      rotation: [0, 0, 0]  # Straight
```

#### Case 2: Coffee Table Height

```
User: "low coffee table"
Modifier extracted: height = 0.45

Original steps affect:
  - TablePlank locations adjusted
  - Leg scales adjusted to shorter length
```

#### Case 3: Table Size

```
User: "large dining table"
Modifiers: scale_factor = 1.5, height = 0.75

All dimensions scaled proportionally.
```

### Implementation Plan

#### Phase 1: Intent Modifier Extraction (Week 1)

1. **IntentModifierExtractor class**
   - Pattern-based extraction
   - Support for common modifiers (size, style, shape)
   - Unit tests

2. **Modifier taxonomy**
   - Define standard modifier names
   - Document modifier effects

#### Phase 2: Workflow Parameter Mapping (Week 1-2)

1. **Extend WorkflowDefinition**
   - Add `param_mapping` field
   - YAML schema for param mappings

2. **Update picnic_table.yaml**
   - Define leg_angle, height, width mappings
   - Test with simple modifiers

#### Phase 3: Parametric Adaptation Engine (Week 2)

1. **ParametricAdaptationEngine class**
   - Step pattern matching
   - Parameter path navigation
   - Transform expressions

2. **Integration with Router**
   - Hook into workflow expansion
   - Logging and telemetry

#### Phase 4: Testing & Refinement (Week 3)

1. **E2E tests**
   - "straight legs" → correct geometry
   - "coffee table" → correct height
   - Combined modifiers

2. **Documentation**
   - Tutorial: Adding param_mapping to workflows
   - Modifier reference guide

---

## YAML Schema Extension

```yaml
# Extended workflow schema

name: my_workflow
description: ...

# NEW: Parameter mapping definitions
param_mapping:
  <modifier_name>:
    description: "Human-readable description"
    default: <default_value>
    range: [<min>, <max>]  # Optional validation
    type: float | int | list | string  # Optional type hint
    affects:
      - step_pattern: "<glob pattern for step names>"
        param_path: "<dot/bracket notation path>"
        transform: "<optional math expression>"

steps:
  - tool: ...
    params: ...
```

### Example: Complete Table Workflow with Mappings

```yaml
name: adaptable_table_workflow
description: Table with configurable legs and dimensions

param_mapping:
  leg_angle:
    description: "Leg angle from vertical (radians)"
    default: 0
    range: [0, 0.5]
    affects:
      - step_pattern: "Leg_*"
        param_path: "rotation[1]"

  leg_style:
    description: "Leg construction style"
    default: "straight"
    options: ["straight", "tapered", "turned"]
    # Complex styles may require step substitution (future)

  table_height:
    description: "Height of table surface"
    default: 0.75
    range: [0.3, 1.2]
    affects:
      - step_pattern: "TableTop*"
        param_path: "location[2]"
      - step_pattern: "Leg_*"
        param_path: "scale[2]"
        transform: "value / 0.75"  # Normalize to default

steps:
  - tool: modeling_create_primitive
    params:
      primitive_type: CUBE
      name: "TableTop"
    description: Create table top

  - tool: modeling_transform_object
    params:
      name: "TableTop"
      location: [0, 0, 0.75]  # Will be adapted by table_height
      scale: [0.4, 0.6, 0.02]

  # Legs with adaptable rotation
  - tool: modeling_create_primitive
    params:
      primitive_type: CUBE
      name: "Leg_FL"

  - tool: modeling_transform_object
    params:
      name: "Leg_FL"
      location: [-0.35, -0.55, 0.375]
      scale: [0.03, 0.03, 0.375]
      rotation: [0, 0, 0]  # Will be adapted by leg_angle
```

---

## Alternative Approaches Considered

### Option A: More Granular Optional Steps (Current - TASK-051)

**Pros:**
- Already implemented
- Simple to understand
- No runtime parameter calculation

**Cons:**
- Cannot modify parameters, only skip/include steps
- Would require multiple workflow variants (straight_leg_table, angled_leg_table, etc.)
- Explosion of workflows for combinations

### Option C: LLM-Based Step Generation

**Pros:**
- Maximum flexibility
- Could generate entirely new workflows

**Cons:**
- Unpredictable results
- High latency (LLM call per adaptation)
- Difficult to validate
- Not suitable for real-time modeling

### Option B: Parametric Adaptation (Recommended)

**Pros:**
- Predictable, deterministic modifications
- Fast execution (no LLM calls)
- Validates against ranges
- Builds on existing workflow structure

**Cons:**
- Requires upfront param_mapping definition
- Limited to pre-defined adaptations
- Cannot create entirely new geometry patterns

---

## Success Criteria

1. **Functional:**
   - "straight legs" produces vertical legs (rotation = 0)
   - "coffee table" produces lower table (height ~0.45m)
   - "large table" scales appropriately

2. **Performance:**
   - Adaptation adds < 10ms to workflow expansion
   - No additional LLM calls required

3. **Usability:**
   - param_mapping syntax documented
   - At least 2 workflows with full mappings (picnic_table, basic_table)

4. **Quality:**
   - 90%+ unit test coverage for new components
   - E2E tests for common adaptation scenarios

---

## Related Tasks

- **TASK-051:** Confidence-Based Workflow Adaptation (prerequisite)
- **TASK-050:** Multi-Embedding Workflow System
- **TASK-046:** Router Semantic Generalization

---

## Files to Create/Modify

### New Files
- `server/router/application/engines/parametric_adapter.py`
- `server/router/application/extractors/intent_modifier_extractor.py`
- `server/router/domain/entities/param_mapping.py`
- `tests/unit/router/application/test_parametric_adapter.py`
- `tests/unit/router/application/test_intent_modifier_extractor.py`

### Modified Files
- `server/router/application/workflows/base.py` - Add param_mapping to WorkflowDefinition
- `server/router/infrastructure/workflow_loader.py` - Parse param_mapping from YAML
- `server/router/application/router.py` - Integrate parametric adaptation
- `server/router/application/workflows/custom/picnic_table.yaml` - Add param_mapping
- `_docs/_ROUTER/WORKFLOWS/creating-workflows-tutorial.md` - Document param_mapping

---

## Notes

This task represents a significant evolution of the router's capabilities, moving from "workflow selection" to "workflow adaptation". It maintains the deterministic, predictable nature of the system while enabling much greater flexibility in meeting user intent.

The key insight is that many geometric variations (straight vs angled, tall vs short, wide vs narrow) can be expressed as **parameter transformations** rather than requiring entirely different workflow definitions.
