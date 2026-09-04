# Geometry Pattern Detector

**Task:** TASK-039-8
**Layer:** Application
**Status:** ✅ Done

## Overview

Detects patterns like tower_like, phone_like, table_like in object geometry.

## File

- `server/router/application/analyzers/geometry_pattern_detector.py`

## Implementation

```python
class GeometryPatternDetector(IPatternDetector):
    def detect(self, context: SceneContext) -> PatternMatchResult
    def detect_pattern(self, context: SceneContext, pattern_type: PatternType) -> DetectedPattern
    def get_best_match(self, context: SceneContext, threshold: float = 0.5) -> Optional[DetectedPattern]
    def get_supported_patterns() -> List[PatternType]
```

## Supported Patterns

| Pattern | Detection Rules | Suggested Workflow |
|---------|----------------|-------------------|
| `TOWER_LIKE` | `is_tall`, `height > width * 3` | `tower_workflow` |
| `PHONE_LIKE` | `is_flat`, `0.4 < aspect_xy < 0.7` | `phone_workflow` |
| `TABLE_LIKE` | `is_flat`, `not is_tall` | `table_workflow` |
| `PILLAR_LIKE` | `is_tall`, cubic in x-y | `pillar_workflow` |
| `WHEEL_LIKE` | `is_flat`, `0.9 < aspect_xy < 1.1` | `wheel_workflow` |
| `BOX_LIKE` | `is_cubic`, `not is_flat`, `not is_tall` | - |

## Usage

```python
detector = GeometryPatternDetector(default_threshold=0.5)

# Detect all patterns
result = detector.detect(context)
print(f"Best match: {result.best_pattern_name}")

# Check specific pattern
tower = detector.detect_pattern(context, PatternType.TOWER_LIKE)
print(f"Tower confidence: {tower.confidence}")

# Get best match above threshold
best = detector.get_best_match(context, threshold=0.7)
if best:
    print(f"Pattern: {best.name}, Workflow: {best.suggested_workflow}")
```

## Pattern Detection Result

```python
DetectedPattern:
    pattern_type: PatternType
    confidence: float           # 0.0 to 1.0
    suggested_workflow: str     # Workflow to trigger
    detection_rules: List[str]  # Rules that matched
    metadata: Dict              # Additional data
```

## Tests

- `tests/unit/router/application/test_geometry_pattern_detector.py` - 24 tests
