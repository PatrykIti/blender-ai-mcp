# 30 - Proportion Inheritance

> **Task:** TASK-046-4 | **Status:** 📋 Planned

---

## Overview

Enables workflows to inherit and combine proportion rules from similar workflows. When modeling an unknown object, this module extracts and combines proportion rules weighted by similarity.

## Interface

```python
@dataclass
class ProportionRule:
    """A single proportion rule."""
    name: str                    # e.g., "bevel_ratio", "inset_ratio"
    value: float                 # The proportion value
    source_workflow: str         # Which workflow this came from
    weight: float = 1.0          # Weight for combining


@dataclass
class InheritedProportions:
    """Collection of inherited proportion rules."""
    rules: Dict[str, ProportionRule]
    sources: List[str]
    total_weight: float

    def get(self, name: str, default: float = 0.0) -> float:
        """Get proportion value by name."""

    def to_dict(self) -> Dict[str, float]:
        """Convert to dict for parameter substitution."""


class ProportionInheritance:
    """Inherits and combines proportion rules from workflows."""

    def register_proportions(self, workflow_name: str, proportions: Dict[str, float]) -> None:
        """Register custom proportions for a workflow."""

    def get_workflow_proportions(self, workflow_name: str) -> Dict[str, float]:
        """Get proportions for a specific workflow."""

    def inherit_proportions(self, similar_workflows: List[Tuple[str, float]]) -> InheritedProportions:
        """Inherit proportions from similar workflows."""

    def apply_to_dimensions(self, proportions: InheritedProportions, dimensions: List[float]) -> Dict[str, float]:
        """Convert relative proportions to absolute values."""
```

## Implementation

**File:** `server/router/application/inheritance/proportion_inheritance.py`

### Built-in Proportion Rules

```python
WORKFLOW_PROPORTIONS = {
    "phone_workflow": {
        "bevel_ratio": 0.04,      # Subtle edge bevel
        "inset_ratio": 0.05,      # Screen border
        "extrude_ratio": 0.40,    # Screen depth
        "corner_radius": 0.02,    # Rounded corners
    },
    "tower_workflow": {
        "bevel_ratio": 0.02,      # Light bevel
        "taper_ratio": 0.15,      # Top narrower than base
        "segment_ratio": 0.25,    # Floor/level height
        "base_ratio": 1.2,        # Base wider than body
    },
    "table_workflow": {
        "bevel_ratio": 0.03,      # Edge bevel
        "leg_ratio": 0.08,        # Leg width vs top
        "top_thickness": 0.05,    # Top thickness ratio
        "leg_inset": 0.10,        # Leg distance from edge
    },
}
```

### Weighted Inheritance Algorithm

```python
def inherit_proportions(self, similar_workflows: List[Tuple[str, float]]) -> InheritedProportions:
    """Combine proportions weighted by similarity."""

    # Collect all rules with weights
    weighted_rules: Dict[str, List[Tuple[float, float, str]]] = {}

    for workflow_name, similarity in similar_workflows:
        proportions = self.get_workflow_proportions(workflow_name)

        for rule_name, value in proportions.items():
            if rule_name not in weighted_rules:
                weighted_rules[rule_name] = []
            weighted_rules[rule_name].append((value, similarity, workflow_name))

    # Calculate weighted average for each rule
    result = InheritedProportions()
    for rule_name, values in weighted_rules.items():
        total_weight = sum(w for _, w, _ in values)
        weighted_value = sum(v * w for v, w, _ in values) / total_weight

        result.rules[rule_name] = ProportionRule(
            name=rule_name,
            value=weighted_value,
            source_workflow=max(values, key=lambda x: x[1])[2],
            weight=total_weight,
        )

    return result
```

### Dimension Application

```python
def apply_to_dimensions(self, proportions: InheritedProportions, dimensions: List[float]) -> Dict[str, float]:
    """Convert relative proportions to absolute values based on object dimensions."""

    x, y, z = dimensions[:3]
    min_dim = min(x, y, z)
    min_xy = min(x, y)

    result = {}
    for name, rule in proportions.rules.items():
        if "bevel" in name or "corner" in name:
            result[name] = rule.value * min_dim
        elif "inset" in name:
            result[name] = rule.value * min_xy
        elif "extrude" in name or "depth" in name:
            result[name] = rule.value * z
        else:
            result[name] = rule.value * min_dim

    return result
```

## Tests

```python
# tests/unit/router/application/inheritance/test_proportion_inheritance.py

def test_inherit_from_single_workflow():
    inheritance = ProportionInheritance()

    result = inheritance.inherit_proportions([("phone_workflow", 1.0)])

    assert "bevel_ratio" in result.rules
    assert result.rules["bevel_ratio"].value == 0.04

def test_weighted_combination():
    inheritance = ProportionInheritance()

    # Table (0.7) + Tower (0.3)
    result = inheritance.inherit_proportions([
        ("table_workflow", 0.7),
        ("tower_workflow", 0.3),
    ])

    # bevel_ratio: table=0.03, tower=0.02
    # weighted = (0.03 * 0.7 + 0.02 * 0.3) / 1.0 = 0.027
    assert abs(result.rules["bevel_ratio"].value - 0.027) < 0.001

def test_apply_to_dimensions():
    inheritance = ProportionInheritance()
    proportions = inheritance.inherit_proportions([("phone_workflow", 1.0)])

    # Phone: 0.1m x 0.05m x 0.008m
    applied = inheritance.apply_to_dimensions(proportions, [0.1, 0.05, 0.008])

    # bevel_ratio (0.04) * min_dim (0.008) = 0.00032
    assert abs(applied["bevel_ratio"] - 0.00032) < 0.0001
```

## Usage

```python
from server.router.application.inheritance import ProportionInheritance

inheritance = ProportionInheritance()

# Get combined proportions for a chair (no chair_workflow)
similar_workflows = [
    ("table_workflow", 0.72),   # Chair has legs like table
    ("tower_workflow", 0.45),   # Vertical structure (backrest)
]

inherited = inheritance.inherit_proportions(similar_workflows)

# Apply to object dimensions
dimensions = [0.4, 0.4, 0.9]  # Chair dimensions
params = inheritance.apply_to_dimensions(inherited, dimensions)

# params now contains absolute values:
# {"bevel_ratio": 0.012, "leg_ratio": 0.032, ...}
```

## See Also

- [29-semantic-workflow-matcher.md](./29-semantic-workflow-matcher.md) - Uses this for generalization
- [09-proportion-calculator.md](./09-proportion-calculator.md) - Related proportion logic
