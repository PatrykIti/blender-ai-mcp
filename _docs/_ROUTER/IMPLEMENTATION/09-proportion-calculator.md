# Proportion Calculator

**Task:** TASK-039-9
**Layer:** Application (utility)
**Status:** ✅ Done

## Overview

Utility for calculating object proportions from dimensions.

## File

- `server/router/application/analyzers/proportion_calculator.py`

## Functions

```python
def calculate_proportions(dimensions: List[float]) -> ProportionInfo
def get_proportion_summary(proportions: ProportionInfo) -> str
def is_phone_like_proportions(proportions: ProportionInfo) -> bool
def is_tower_like_proportions(proportions: ProportionInfo) -> bool
def is_table_like_proportions(proportions: ProportionInfo) -> bool
def is_wheel_like_proportions(proportions: ProportionInfo) -> bool
def get_dimensions_from_dict(data: Dict) -> Optional[List[float]]
```

## Calculated Proportions

```python
ProportionInfo:
    aspect_xy: float      # x / y ratio
    aspect_xz: float      # x / z ratio
    aspect_yz: float      # y / z ratio
    is_flat: bool         # z < min(x, y) * 0.2
    is_tall: bool         # z > max(x, y) * 2
    is_wide: bool         # x > max(y, z) * 2
    is_cubic: bool        # max/min < 1.5
    dominant_axis: str    # "x", "y", or "z"
    volume: float         # x * y * z
    surface_area: float   # 2 * (xy + yz + xz)
```

## Usage

```python
# Calculate proportions
props = calculate_proportions([0.4, 0.8, 0.05])
print(f"Flat: {props.is_flat}")        # True
print(f"Aspect XY: {props.aspect_xy}") # 0.5

# Get summary
summary = get_proportion_summary(props)  # "flat"

# Check specific shape
if is_phone_like_proportions(props):
    print("This is phone-like!")

# Extract dimensions from various formats
dims = get_dimensions_from_dict({"dimensions": [1, 2, 3]})
dims = get_dimensions_from_dict({"x": 1, "y": 2, "z": 3})
dims = get_dimensions_from_dict({"size": [1, 2, 3]})
```

## Shape Examples

| Dimensions | Flags | Summary |
|------------|-------|---------|
| `[1, 1, 1]` | `is_cubic=True` | cubic |
| `[2, 2, 0.1]` | `is_flat=True` | flat |
| `[0.3, 0.3, 3]` | `is_tall=True` | tall |
| `[5, 1, 1]` | `is_wide=True` | wide |
| `[0.4, 0.8, 0.05]` | `is_flat=True` | flat (phone-like) |

## Tests

- `tests/unit/router/application/test_proportion_calculator.py` - 31 tests
