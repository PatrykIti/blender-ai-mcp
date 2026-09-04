# Changelog 66: Router Tool Override Engine

**Date:** 2025-12-01
**Type:** Feature
**Task:** TASK-039-12

## Summary

Implemented the Tool Override Engine for the Router Supervisor, providing pattern-based tool replacement.

## Changes

### New Files

- `server/router/application/engines/tool_override_engine.py` - Main implementation
- `tests/unit/router/application/test_tool_override_engine.py` - 30 unit tests

### Features

1. **Pattern-Based Overrides**
   - Checks if detected geometry pattern suggests tool replacement
   - Returns list of replacement tools with parameters

2. **Default Override Rules**
   - `extrude_for_screen` - On phone-like pattern, adds inset before extrude
   - `subdivide_tower` - On tower-like pattern, adds top selection and scaling

3. **Rule Management**
   - Register custom override rules
   - Remove existing rules
   - Query available rules

### API

```python
engine = ToolOverrideEngine(config=RouterConfig())
decision = engine.check_override(tool_name, params, context, pattern)
if decision.should_override:
    for tool in decision.replacement_tools:
        # Execute replacement tools
```

## Related

- Part of Phase 3: Tool Processing Engines
- Implements `IOverrideEngine` interface
