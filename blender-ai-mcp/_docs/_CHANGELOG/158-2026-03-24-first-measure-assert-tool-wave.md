# 158 - 2026-03-24: First measure/assert tool wave

**Status**: ✅ Completed  
**Type**: Feature / Truth Layer  
**Task**: TASK-116

---

## Summary

Implemented the first deterministic scene truth-layer tool family:

- `scene_measure_distance`
- `scene_measure_dimensions`
- `scene_measure_gap`
- `scene_measure_alignment`
- `scene_measure_overlap`

The rollout includes:

- addon-side measurement handlers and RPC registration
- server/domain/application wiring and dispatcher support
- MCP structured contracts and public tool exposure
- router metadata for the new scene tools
- unit and E2E regression coverage
- README, MCP docs, addon docs, and tool inventory updates
