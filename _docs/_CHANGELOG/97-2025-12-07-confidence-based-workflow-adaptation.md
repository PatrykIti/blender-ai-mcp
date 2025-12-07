# 97 - Confidence-Based Workflow Adaptation (TASK-051)

**Date:** 2025-12-07

## Summary

Implemented confidence-based workflow adaptation that dynamically adjusts workflow steps based on match confidence level. When the user asks for "simple table with 4 legs", the router now correctly skips bench steps instead of executing the full 49-step picnic table workflow.

## Problem

The router had sophisticated components (confidence levels, `find_best_match_with_confidence()`, feedback learning) but they were NOT connected to workflow execution:

```
User: "simple table with 4 legs"
Before: Executed ALL 49 steps (including 16 bench steps)
After:  Executes ~33 core steps (skips benches)
```

## Solution

### New Components

| Component | File | Purpose |
|-----------|------|---------|
| **WorkflowAdapter** | `engines/workflow_adapter.py` | Adapts workflows based on confidence |
| **AdaptationResult** | `engines/workflow_adapter.py` | Tracks adaptation decisions |

### Confidence-Based Adaptation Strategy

| Confidence Level | Strategy | Behavior |
|------------------|----------|----------|
| **HIGH** (≥0.90) | `FULL` | Execute ALL steps (no adaptation) |
| **MEDIUM** (≥0.75) | `FILTERED` | Core + tag-matching optional steps |
| **LOW** (≥0.60) | `CORE_ONLY` | Core steps only (skip all optional) |
| **NONE** (<0.60) | `CORE_ONLY` | Core steps only (fallback) |

### WorkflowStep Extensions

```yaml
# New fields in WorkflowStep
- tool: modeling_create_primitive
  params:
    primitive_type: CUBE
    name: "BenchLeft"
  optional: true          # NEW: Can be skipped
  tags: ["bench", "seating"]  # NEW: For MEDIUM confidence filtering
```

## Files Changed

### New Files
- `server/router/application/engines/workflow_adapter.py` (~230 lines)
- `tests/unit/router/application/test_workflow_adapter.py` (~450 lines, 20 tests)

### Modified Files
- `server/router/application/workflows/base.py` - Added `optional` and `tags` to WorkflowStep
- `server/router/infrastructure/workflow_loader.py` - Parse new YAML fields
- `server/router/application/workflows/custom/picnic_table.yaml` - Marked 16 bench steps as optional
- `server/router/application/matcher/semantic_workflow_matcher.py` - Added `confidence_level`, `requires_adaptation`, `needs_adaptation()`
- `server/router/infrastructure/config.py` - Added `enable_workflow_adaptation`, `adaptation_semantic_threshold`
- `server/router/application/router.py` - Integrated WorkflowAdapter
- `server/router/application/engines/__init__.py` - Export new classes
- `tests/unit/router/application/matcher/test_semantic_workflow_matcher.py` - Updated tests

## Configuration

```python
# New config options in RouterConfig
enable_workflow_adaptation: bool = True      # Enable adaptation
adaptation_semantic_threshold: float = 0.6  # For MEDIUM confidence tag matching
```

## Usage Examples

### HIGH Confidence - Full Workflow
```python
# User: "create a picnic table"
# Result: All 49 steps executed (tables + benches)
adaptation_result.adaptation_strategy == "FULL"
adaptation_result.adapted_step_count == 49
```

### LOW Confidence - Core Only
```python
# User: "simple table with 4 legs"
# Result: Only core steps (~33), benches skipped
adaptation_result.adaptation_strategy == "CORE_ONLY"
adaptation_result.skipped_steps == ["Create left bench", "Position left bench", ...]
```

### MEDIUM Confidence - Filtered
```python
# User: "table with benches"
# Result: Core + bench steps (tag match on "bench")
adaptation_result.adaptation_strategy == "FILTERED"
adaptation_result.included_optional == ["BenchLeft", "BenchRight", ...]
```

## Tests

- 20 new unit tests for WorkflowAdapter
- Updated 3 tests in test_semantic_workflow_matcher.py
- All 905+ router tests passing

## Technical Details

### Adaptation Flow

```
1. SemanticWorkflowMatcher.match() returns MatchResult with:
   - confidence_level: HIGH/MEDIUM/LOW/NONE
   - requires_adaptation: bool

2. Router._expand_triggered_workflow() checks needs_adaptation()

3. WorkflowAdapter.adapt() filters steps:
   - HIGH: Return all steps
   - MEDIUM: Core + _filter_by_relevance(optional_steps)
   - LOW/NONE: Core steps only

4. _filter_by_relevance() uses:
   - Tag matching (fast, keyword in prompt)
   - Semantic similarity fallback (if no tags)
```

### Tag Matching for MEDIUM Confidence

```python
# Step has tags: ["bench", "seating", "side"]
# User prompt: "table with bench"
# Result: "bench" in prompt → step included
```

## Related Tasks

- TASK-046: Router Semantic Generalization (added confidence levels)
- TASK-050: Multi-Embedding Workflow System (find_best_match_with_confidence)
- TASK-047: LanceDB Migration (vector search)

## See Also

- [TASK-051 Details](../_TASKS/TASK-051_Confidence_Based_Workflow_Adaptation.md)
- [WorkflowAdapter Implementation](../_ROUTER/IMPLEMENTATION/32-workflow-adapter.md)
