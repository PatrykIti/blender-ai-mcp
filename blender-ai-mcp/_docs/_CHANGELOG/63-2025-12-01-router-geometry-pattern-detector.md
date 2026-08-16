# 63 - Router Geometry Pattern Detector

**Date:** 2025-12-01
**Task:** TASK-039-8
**Type:** Feature

## Summary

Implemented geometry pattern detection for router workflow triggers.

## Changes

### Added
- `server/router/application/analyzers/geometry_pattern_detector.py` - GeometryPatternDetector class
- `tests/unit/router/application/test_geometry_pattern_detector.py` - 24 unit tests

### Supported Patterns
- TOWER_LIKE - tall vertical structures
- PHONE_LIKE - flat rectangular thin objects
- TABLE_LIKE - flat horizontal surfaces
- PILLAR_LIKE - tall cubic structures
- WHEEL_LIKE - flat circular objects
- BOX_LIKE - roughly cubic shapes

### Features
- Detect all patterns with confidence scores
- Get best match above threshold
- Suggested workflow for each pattern
- Detection rules metadata

## Tests

- 24 new tests for GeometryPatternDetector
