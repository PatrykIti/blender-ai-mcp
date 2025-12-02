# 82 - TASK-041 Created: Router YAML Workflow Integration

**Date:** 2025-12-02
**Status:** Task Created
**Task:** TASK-041 (Router YAML Workflow Integration)

## Summary

Created detailed task specification for integrating YAML-based custom workflows into the Router Supervisor system. This task bridges the gap between existing components (WorkflowLoader, WorkflowRegistry, WorkflowExpansionEngine) that are currently not connected.

## Problem Identified

```
WorkflowLoader (parses YAML) ──X──▶ WorkflowRegistry (central registry)
                                          │
                                          X (not used by)
                                          │
WorkflowExpansionEngine ◀── uses hardcoded PREDEFINED_WORKFLOWS dict
```

## Task Breakdown

| Phase | Tasks | Priority | Est. Time |
|-------|-------|----------|-----------|
| **P0: Connect YAML** | 3 tasks | 🔴 High | 2.5h |
| **P1: Auto-Trigger** | 3 tasks | 🔴 High | 3.5h |
| **P2: Expressions** | 3 tasks | 🟡 Medium | 3.5h |
| **P3: Conditions** | 3 tasks | 🟡 Medium | 3.5h |
| **P4: Proportions** | 2 tasks | 🟢 Low | 1.5h |
| **Testing/Docs** | 2 tasks | 🟡 Medium | 3h |
| **TOTAL** | **16 tasks** | | **~17.5h** |

## New Components to Create

| Component | Purpose |
|-----------|---------|
| `WorkflowTriggerer` | Determines when to trigger workflows (keywords, patterns, tools) |
| `ExpressionEvaluator` | Evaluates `$CALCULATE(...)` expressions safely |
| `ConditionEvaluator` | Evaluates boolean conditions for step execution |
| `ProportionResolver` | Resolves `$AUTO_*` params relative to dimensions |

## Target Workflow YAML Format

```yaml
name: house_simple
trigger_keywords: ["house", "building"]
steps:
  - tool: modeling_create_primitive
    params: { type: "CUBE" }

  - tool: system_set_mode
    params: { mode: "EDIT" }
    condition: "current_mode != 'EDIT'"  # Conditional execution

  - tool: mesh_bevel
    params:
      width: "$CALCULATE(min_dim * 0.02)"  # Dynamic expression
      segments: 2
```

## Files Created

- `_docs/_TASKS/TASK-041_Router_YAML_Workflow_Integration.md` - Full task specification

## Related

- Parent: TASK-039 (Router Supervisor Implementation)
- Changelog: 81-2025-12-02-router-mcp-tools-integration.md
