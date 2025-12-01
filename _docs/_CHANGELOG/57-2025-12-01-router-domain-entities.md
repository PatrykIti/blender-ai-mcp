# Changelog: Router Domain Entities

**Date:** 2025-12-01
**Task:** TASK-039-2
**Type:** Feature

---

## Summary

Implemented domain entities for the Router Supervisor module - pure data classes with no external dependencies.

---

## New Files

| File | Description |
|------|-------------|
| `server/router/domain/entities/tool_call.py` | InterceptedToolCall, CorrectedToolCall, ToolCallSequence |
| `server/router/domain/entities/scene_context.py` | ObjectInfo, TopologyInfo, ProportionInfo, SceneContext |
| `server/router/domain/entities/pattern.py` | PatternType, DetectedPattern, PatternMatchResult |
| `server/router/domain/entities/firewall_result.py` | FirewallAction, FirewallResult, FirewallViolation |
| `server/router/domain/entities/override_decision.py` | OverrideReason, ReplacementTool, OverrideDecision |
| `tests/unit/router/domain/test_entities.py` | 32 unit tests |

---

## Entities Summary

### Tool Call
- `InterceptedToolCall` - Captured LLM tool call
- `CorrectedToolCall` - Tool call after corrections
- `ToolCallSequence` - Sequence of calls to execute

### Scene Context
- `ObjectInfo` - Single object information
- `TopologyInfo` - Mesh topology (verts, edges, faces)
- `ProportionInfo` - Calculated proportions
- `SceneContext` - Complete scene state

### Pattern
- `PatternType` - Enum of known patterns (tower_like, phone_like, etc.)
- `DetectedPattern` - Pattern detection result
- `PatternMatchResult` - Multiple pattern match results

### Firewall
- `FirewallAction` - Actions (allow, block, modify, auto_fix)
- `FirewallResult` - Validation result with pre-steps

### Override
- `ReplacementTool` - Replacement tool with param inheritance
- `OverrideDecision` - Override/workflow expansion decision

---

## Tests

32 unit tests covering all entities:
- Serialization (to_dict, from_dict)
- Property methods
- Factory methods
- Parameter resolution

---

## Next Steps

- TASK-039-3: Domain Interfaces
