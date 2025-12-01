# 60 - Router Configuration

**Date:** 2025-12-01
**Task:** TASK-039-5
**Type:** Feature

## Summary

Added configuration system for Router Supervisor behavior.

## Changes

### Added
- `server/router/infrastructure/config.py` - RouterConfig dataclass
- `tests/unit/router/infrastructure/test_config.py` - 16 unit tests

### Configuration Options
- Correction settings (auto_mode_switch, auto_selection, clamp_parameters)
- Override settings (enable_overrides, enable_workflow_expansion)
- Firewall settings (block_invalid_operations, auto_fix_mode_violations)
- Thresholds (embedding_threshold, bevel_max_ratio, subdivide_max_cuts)
- Advanced settings (cache_scene_context, cache_ttl_seconds, max_workflow_steps, log_decisions)

## Tests

- 16 new tests for RouterConfig
