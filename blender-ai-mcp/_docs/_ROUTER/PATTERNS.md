# Router Patterns Reference

Complete reference for geometry pattern detection in Router Supervisor.

---

## How Pattern Detection Works

Router detects object geometry patterns based on **proportions** (dimensions and aspect ratios).

```
Object Dimensions
       ↓
┌────────────────────┐
│ ProportionInfo     │  → is_flat, is_tall, is_cubic, is_wide
│ (calculated)       │  → aspect_xy, aspect_xz, aspect_yz
└────────────────────┘
       ↓
┌────────────────────┐
│ GeometryPattern    │  → Check rules for each pattern
│ Detector           │  → Calculate confidence scores
└────────────────────┘
       ↓
┌────────────────────┐
│ PatternMatchResult │  → best_match (highest confidence)
│                    │  → all patterns with scores
└────────────────────┘
```

---

## Supported Patterns

### Overview

| Pattern | Description | Primary Use Case |
|---------|-------------|------------------|
| `tower_like` | Tall vertical structure | Buildings, towers, pillars |
| `phone_like` | Flat rectangular thin | Phones, tablets, cards |
| `table_like` | Flat horizontal surface | Tables, platforms |
| `pillar_like` | Tall cubic structure | Columns, posts |
| `wheel_like` | Flat circular object | Wheels, discs, coins |
| `box_like` | Roughly cubic shape | Boxes, cubes |
| `sphere_like` | Spherical shape | Balls, orbs |
| `cylinder_like` | Cylindrical shape | Pipes, tubes |

---

## Pattern Detection Rules

### 1. TOWER_LIKE

**Description:** Tall vertical structure (height >> width and depth)

**Detection Rules:**
```
- is_tall = True
- height > width × 3  (aspect_xz < 0.33)
- height > depth × 3  (aspect_yz < 0.33)
```

**Confidence Scoring:**
| Rule | Points |
|------|--------|
| `is_tall` | +0.4 |
| `height > width × 3` | +0.3 |
| `height > depth × 3` | +0.3 |

**Example Dimensions:**
```python
# Tower-like (confidence: 1.0)
scale = [0.3, 0.3, 2.0]  # Z = 6.7× larger than X/Y

# Not tower-like
scale = [1.0, 1.0, 1.5]  # Z only 1.5× larger
```

**Suggested Workflow:** `tower_workflow`

---

### 2. PHONE_LIKE

**Description:** Flat rectangular thin object (smartphone shape)

**Detection Rules:**
```
- is_flat = True
- 0.4 < aspect_xy < 0.7  (rectangular, not square)
- thin (Z is not dominant axis)
```

**Confidence Scoring:**
| Rule | Points |
|------|--------|
| `is_flat` | +0.4 |
| `0.4 < aspect_xy < 0.7` | +0.4 |
| `thin` | +0.2 |

**Example Dimensions:**
```python
# Phone-like (confidence: 1.0)
scale = [0.4, 0.8, 0.05]  # Flat, rectangular (0.5 ratio)

# Not phone-like (too square)
scale = [0.5, 0.5, 0.05]  # Square aspect ratio
```

**Suggested Workflow:** `phone_workflow`

---

### 3. TABLE_LIKE

**Description:** Flat horizontal surface

**Detection Rules:**
```
- is_flat = True
- is_tall = False
- Bonus: is_wide or aspect_xy > 0.8
```

**Confidence Scoring:**
| Rule | Points |
|------|--------|
| `is_flat` | +0.5 |
| `not is_tall` | +0.3 |
| `wide surface` | +0.2 |

**Example Dimensions:**
```python
# Table-like (confidence: 1.0)
scale = [2.0, 1.5, 0.1]  # Wide, flat surface

# Not table-like (too tall)
scale = [1.0, 1.0, 1.0]  # Cube
```

**Suggested Workflow:** `table_workflow`

---

### 4. PILLAR_LIKE

**Description:** Tall structure with square cross-section

**Detection Rules:**
```
- is_tall = True
- 0.7 < aspect_xy < 1.3  (cubic in X-Y plane)
```

**Confidence Scoring:**
| Rule | Points |
|------|--------|
| `is_tall` | +0.5 |
| `cubic in x-y plane` | +0.5 |

**Example Dimensions:**
```python
# Pillar-like (confidence: 1.0)
scale = [0.3, 0.3, 2.0]  # Tall with square base

# Not pillar-like (rectangular base)
scale = [0.5, 0.2, 2.0]  # Tall but not square base
```

**Suggested Workflow:** `pillar_workflow`

---

### 5. WHEEL_LIKE

**Description:** Flat circular object

**Detection Rules:**
```
- is_flat = True
- 0.9 < aspect_xy < 1.1  (circular in X-Y plane)
```

**Confidence Scoring:**
| Rule | Points |
|------|--------|
| `is_flat` | +0.4 |
| `0.9 < aspect_xy < 1.1` | +0.6 |

**Example Dimensions:**
```python
# Wheel-like (confidence: 1.0)
scale = [1.0, 1.0, 0.2]  # Flat disc

# Not wheel-like (not circular)
scale = [1.0, 0.5, 0.2]  # Flat but oval
```

**Suggested Workflow:** `wheel_workflow`

---

### 6. BOX_LIKE

**Description:** Roughly cubic shape

**Detection Rules:**
```
- is_cubic = True
- is_flat = False
- is_tall = False
```

**Confidence Scoring:**
| Rule | Points |
|------|--------|
| `is_cubic` | +0.5 |
| `not is_flat` | +0.25 |
| `not is_tall` | +0.25 |

**Example Dimensions:**
```python
# Box-like (confidence: 1.0)
scale = [1.0, 1.0, 1.0]  # Perfect cube

# Still box-like (confidence: 0.75)
scale = [1.0, 0.8, 1.2]  # Slightly irregular
```

**Suggested Workflow:** None (default)

---

## Proportion Calculation

Proportions are calculated from object dimensions:

```python
# From dimensions [x, y, z]
aspect_xy = x / y  # Width to depth ratio
aspect_xz = x / z  # Width to height ratio
aspect_yz = y / z  # Depth to height ratio

# Flags
is_flat = z < min(x, y) * 0.5
is_tall = z > max(x, y) * 2.0
is_wide = x > y * 1.5 or y > x * 1.5
is_cubic = 0.7 < aspect_xy < 1.3 and 0.7 < aspect_xz < 1.3
```

---

## Using Patterns in Code

### Detect Patterns

```python
from server.router.application.analyzers.geometry_pattern_detector import GeometryPatternDetector
from server.router.domain.entities.scene_context import SceneContext

detector = GeometryPatternDetector(default_threshold=0.5)

# Full detection (all patterns)
result = detector.detect(context)
print(f"Best match: {result.best_pattern_name}")
print(f"Confidence: {result.best_match.confidence}")

# Check specific pattern
from server.router.domain.entities.pattern import PatternType
phone = detector.detect_pattern(context, PatternType.PHONE_LIKE)
if phone.confidence > 0.7:
    print("This is definitely a phone-like object!")
```

### Pattern in Override Rules

```python
# In tool_override_engine.py
self.register_rule(
    rule_name="extrude_on_phone",
    trigger_tool="mesh_extrude_region",
    trigger_pattern="phone_like",  # Pattern name
    replacement_tools=[
        {"tool_name": "mesh_inset", "params": {"thickness": 0.03}},
        {"tool_name": "mesh_extrude_region", "inherit_params": ["move"]},
    ],
)
```

---

## Confidence Thresholds

| Threshold | Usage |
|-----------|-------|
| `0.5` | Default - triggers pattern-based workflows |
| `0.7` | High confidence - used for `is_confident` property |
| `0.3` | Low - pattern detected but not dominant |

**Recommendation:** Use 0.5+ for workflow triggers, 0.7+ for critical decisions.

---

## Adding Custom Patterns

### 1. Add Pattern Type

```python
# server/router/domain/entities/pattern.py
class PatternType(Enum):
    # ... existing ...
    MY_CUSTOM = "my_custom"  # Add new pattern
```

### 2. Add Pattern Rules

```python
# server/router/domain/entities/pattern.py
PATTERN_RULES[PatternType.MY_CUSTOM] = {
    "description": "My custom pattern",
    "rules": ["custom_rule_1", "custom_rule_2"],
    "suggested_workflow": "my_workflow",
}
```

### 3. Implement Detection

```python
# server/router/application/analyzers/geometry_pattern_detector.py

def _detect_my_custom(self, proportions: ProportionInfo) -> DetectedPattern:
    """Detect my custom pattern."""
    rules_matched = []
    confidence = 0.0

    if some_condition:
        rules_matched.append("custom_rule_1")
        confidence += 0.5

    if another_condition:
        rules_matched.append("custom_rule_2")
        confidence += 0.5

    return DetectedPattern(
        pattern_type=PatternType.MY_CUSTOM,
        confidence=min(confidence, 1.0),
        suggested_workflow=PATTERN_RULES.get(PatternType.MY_CUSTOM, {}).get("suggested_workflow"),
        detection_rules=rules_matched,
    )
```

### 4. Register in Detector

```python
# In get_supported_patterns()
def get_supported_patterns(self) -> List[PatternType]:
    return [
        # ... existing ...
        PatternType.MY_CUSTOM,
    ]

# In detect_pattern()
elif pattern_type == PatternType.MY_CUSTOM:
    return self._detect_my_custom(proportions)
```

---

## Pattern-Workflow Mapping

| Pattern | Workflow | Operations |
|---------|----------|------------|
| `tower_like` | `tower_workflow` | Taper, subdivide, add detail |
| `phone_like` | `phone_workflow` | Screen cutout (inset + extrude) |
| `table_like` | `table_workflow` | Leg extrusion |
| `pillar_like` | `pillar_workflow` | Detail subdivisions |
| `wheel_like` | `wheel_workflow` | Spoke patterns |
| `box_like` | None | Default handling |
| `sphere_like` | None | Default handling |
| `cylinder_like` | None | Default handling |

---

## See Also

- [CONFIGURATION.md](./CONFIGURATION.md) - Threshold settings
- [QUICK_START.md](./QUICK_START.md) - Getting started
- [WORKFLOWS/](./WORKFLOWS/) - Workflow definitions
- [API.md](./API.md) - Full API reference
