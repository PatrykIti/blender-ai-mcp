# 62 - Router Scene Context Analyzer

**Date:** 2025-12-01
**Task:** TASK-039-7
**Type:** Feature

## Summary

Implemented Blender scene state analysis for router decision making.

## Changes

### Added
- `server/router/application/analyzers/scene_context_analyzer.py` - SceneContextAnalyzer class
- `tests/unit/router/application/test_scene_context_analyzer.py` - 20 unit tests

### Features
- Query scene via RPC client
- Cache results with configurable TTL
- Extract mode, active object, selection, topology, proportions
- Calculate proportions automatically from dimensions
- Graceful fallback on RPC errors
- analyze_from_data() for testing/offline use

## Tests

- 20 new tests for SceneContextAnalyzer
