# 78 - Router E2E Test Fixes

**Date:** 2025-12-02
**TASK:** TASK-039 (Router Supervisor Implementation)
**Status:** Done

## Problem

After implementing the Router Supervisor, 6 E2E tests were failing due to several different bugs:

1. **Incorrect RPC parameter** - tests used `{"type": "CUBE"}` instead of `{"primitive_type": "CUBE"}`
2. **Incorrect access to ProportionInfo** - tests used `.get()` (dict method) on a dataclass
3. **Incorrect pattern expectations** - the test looked for "flat" in pattern names, but such a pattern does not exist
4. **Incorrect logger in the telemetry test** - the test used the global singleton instead of the router's logger

## Fixes

### 1. RPC parameter `primitive_type`

**Problem:** `ModelingHandler.create_primitive()` expects `primitive_type`, not `type`

**Files:**
- `tests/e2e/router/test_pattern_detection.py`
- `tests/e2e/router/test_full_pipeline.py`
- `tests/e2e/router/test_router_scenarios.py`
- `tests/e2e/router/test_workflow_execution.py`

**Change:**
```python
# Before
rpc_client.send_request("modeling.create_primitive", {"type": "CUBE"})

# After
rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
```

### 2. Access to ProportionInfo attributes

**Problem:** `ProportionInfo` is a dataclass, not a dict - it does not have the `.get()` method

**File:** `tests/e2e/router/test_pattern_detection.py:124-153`

**Change:**
```python
# Before
context.proportions.get("is_flat", False)
context.proportions.get("aspect_xz", 1)
context.proportions.get("is_tall", False)
context.proportions.get("dominant_axis")

# After
context.proportions.is_flat
context.proportions.aspect_xz
context.proportions.is_tall
context.proportions.dominant_axis
```

**Additional change:** Added a fallback when dimensions return the default [1,1,1] (Blender distinguishes scale from dimensions)

### 3. Pattern expectations for flat objects

**Problem:** The test looked for patterns containing "flat" or "phone" in the name, but:
- There is no `flat_like` pattern - `is_flat` is only a boolean flag
- Patterns indicating flat objects are: `phone_like`, `table_like`, `wheel_like`

**File:** `tests/e2e/router/test_pattern_detection.py:46-51`

**Change:**
```python
# Before
has_flat = any("flat" in name.lower() for name in pattern_names)
has_phone = any("phone" in name.lower() for name in pattern_names)
assert has_flat or has_phone

# After
flat_patterns = {"phone_like", "table_like", "wheel_like"}
has_flat_pattern = any(name in flat_patterns for name in pattern_names)
assert has_flat_pattern
```

### 4. Logger in telemetry test

**Problem:** `SupervisorRouter` creates its own instance `RouterLogger()` (line 90 in router.py), it does not use the global singleton `get_router_logger()`

**File:** `tests/e2e/router/test_full_pipeline.py:70-86`

**Change:**
```python
# Before
from server.router.infrastructure.logger import get_router_logger
logger = get_router_logger()
logger.clear_events()
events = logger.get_events()

# After
router.logger.clear_events()
events = router.logger.get_events()
```

## Result

- **Before:** 32 passed, 6 failed
- **After:** 38 passed, 0 failed

## List of changed files

| File | Type of change |
|------|----------------|
| `tests/e2e/router/test_pattern_detection.py` | Fixed RPC parameter, access to ProportionInfo, pattern expectations |
| `tests/e2e/router/test_full_pipeline.py` | Fixed RPC parameter, telemetry logger |
| `tests/e2e/router/test_router_scenarios.py` | Fixed RPC parameter |
| `tests/e2e/router/test_workflow_execution.py` | Fixed RPC parameter |
