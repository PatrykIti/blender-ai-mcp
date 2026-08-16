# Router Configuration

**Task:** TASK-039-5
**Layer:** Infrastructure
**Status:** ✅ Done

## Overview

Configuration dataclass for Router Supervisor behavior settings.

## File

- `server/router/infrastructure/config.py`

## Implementation

```python
@dataclass
class RouterConfig:
    # Correction settings
    auto_mode_switch: bool = True
    auto_selection: bool = True
    clamp_parameters: bool = True

    # Override settings
    enable_overrides: bool = True
    enable_workflow_expansion: bool = True

    # Firewall settings
    block_invalid_operations: bool = True
    auto_fix_mode_violations: bool = True

    # Thresholds
    embedding_threshold: float = 0.40
    bevel_max_ratio: float = 0.5
    subdivide_max_cuts: int = 6

    # Advanced settings
    cache_scene_context: bool = True
    cache_ttl_seconds: float = 1.0
    max_workflow_steps: int = 20
    log_decisions: bool = True
```

## Features

- Default values for all settings
- `to_dict()` serialization
- `from_dict()` deserialization with unknown key handling
- Roundtrip serialization support

## Configuration Groups

| Group | Settings | Description |
|-------|----------|-------------|
| Correction | `auto_mode_switch`, `auto_selection`, `clamp_parameters` | Auto-fix LLM mistakes |
| Override | `enable_overrides`, `enable_workflow_expansion` | Tool replacement |
| Firewall | `block_invalid_operations`, `auto_fix_mode_violations` | Validation |
| Thresholds | `embedding_threshold`, `bevel_max_ratio`, `subdivide_max_cuts` | Limits |
| Advanced | `cache_scene_context`, `cache_ttl_seconds`, `max_workflow_steps`, `log_decisions` | Performance |

## Tests

- `tests/unit/router/infrastructure/test_config.py` - 16 tests
