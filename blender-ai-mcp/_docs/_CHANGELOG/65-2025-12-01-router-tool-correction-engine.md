# Changelog 65: Router Tool Correction Engine

**Date:** 2025-12-01
**Type:** Feature
**Task:** TASK-039-10, TASK-039-11

## Summary

Implemented the Tool Correction Engine for the Router Supervisor, providing automatic mode switching, selection handling, and parameter clamping.

## Changes

### New Files

- `server/router/application/engines/tool_correction_engine.py` - Main implementation
- `tests/unit/router/application/test_tool_correction_engine.py` - 44 unit tests

### Features

1. **Mode Auto-Switch**
   - Detects when tool requires different mode (OBJECT, EDIT, SCULPT)
   - Automatically injects mode switch command as pre-step

2. **Selection Auto-Fix**
   - Detects tools that require geometry selection
   - Adds `mesh_select(action="all")` when no selection exists

3. **Parameter Clamping**
   - Clamps parameters to valid ranges
   - Dimension-relative clamping for bevel width
   - Configurable limits via PARAM_LIMITS dict

### API

```python
engine = ToolCorrectionEngine(config=RouterConfig())
corrected_call, pre_steps = engine.correct(tool_name, params, context)
```

## Related

- Part of Phase 3: Tool Processing Engines
- Implements `ICorrectionEngine` interface
