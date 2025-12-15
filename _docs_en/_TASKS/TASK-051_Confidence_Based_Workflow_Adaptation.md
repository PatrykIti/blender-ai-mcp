# TASK-051: Confidence-Based Workflow Adaptation

| Status | Priority | Complexity | Completion Date |
|--------|----------|------------|-----------------|
| ✅ Done | 🔴 High | Medium | 2025-12-07 |

---

## Problem
The router has built components (confidence levels, `find_best_match_with_confidence()`, feedback learning), but **they are not connected**:
1. `find_best_match_with_confidence()` exists but is never called
2. Confidence levels (HIGH≥0.90, MEDIUM≥0.75, LOW≥0.60) defined but unused
3. "simple table with 4 legs" → executes the FULL picnic_table_workflow with benches
4. Feedback learning collects data but does not use it

## Solution: Workflow Adaptation Engine

### Concept
```
Confidence Level → Adaptation Strategy
─────────────────────────────────────────
HIGH (≥0.90)   → Execute ALL steps
MEDIUM (≥0.75) → Core + semantically relevant optional
LOW (≥0.60)    → Only CORE steps (skip optional)
NONE (<0.60)   → Only CORE steps (fallback)
```

### Changes in files

#### 1. `server/router/application/workflows/base.py`
Add `optional` and `tags` fields to `WorkflowStep`:
```python
@dataclass
class WorkflowStep:
    tool: str
    params: Dict[str, Any]
    description: Optional[str] = None
    condition: Optional[str] = None
    optional: bool = False  # NEW
    tags: List[str] = field(default_factory=list)  # NEW
```

#### 2. `server/router/infrastructure/workflow_loader.py`
Update `_parse_step()` to parse the new fields from YAML.

#### 3. `server/router/application/workflows/custom/picnic_table.yaml`
Mark 16 bench-related steps as `optional: true, tags: ["bench", "seating"]`:
- BenchLeft_Inner/Outer (4 steps)
- BenchRight_Inner/Outer (4 steps)
- BenchBack_Inner/Outer (4 steps)
- BenchFront_Inner/Outer (4 steps)

#### 4. `server/router/application/matcher/semantic_workflow_matcher.py`
Update `MatchResult` dataclass:
```python
@dataclass
class MatchResult:
    # ... existing ...
    confidence_level: str = "NONE"  # NEW
    requires_adaptation: bool = False  # NEW
```

In `match()` replace `find_best_match()` with `find_best_match_with_confidence()`.

#### 5. NEW: `server/router/application/engines/workflow_adapter.py`
New engine (~230 lines):
```python
class WorkflowAdapter:
    def adapt(
        self,
        definition: WorkflowDefinition,
        confidence_level: str,
        user_prompt: str,
    ) -> Tuple[List[WorkflowStep], AdaptationResult]:
        if confidence_level == "HIGH":
            return all_steps

        core_steps = [s for s in steps if not s.optional]
        optional_steps = [s for s in steps if s.optional]

        if confidence_level in ("LOW", "NONE"):
            return core_steps  # Skip all optional

        if confidence_level == "MEDIUM":
            relevant = self._filter_by_relevance(optional_steps, user_prompt)
            return core_steps + relevant

    def _filter_by_relevance(self, steps, prompt) -> List[WorkflowStep]:
        """Fallback: first tag matching, then semantic similarity."""
        relevant = []
        for step in steps:
            # 1. Tag matching (fast)
            if step.tags and any(tag.lower() in prompt.lower() for tag in step.tags):
                relevant.append(step)
                continue
            # 2. Semantic similarity (fallback for steps without tags)
            if step.description and self._classifier:
                sim = self._classifier.similarity(prompt, step.description)
                if sim >= self._semantic_threshold:
                    relevant.append(step)
        return relevant
```

#### 6. `server/router/application/router.py`
In `_expand_triggered_workflow()` add:
```python
if self.config.enable_workflow_adaptation and match_result.requires_adaptation:
    adapted_steps, result = self._workflow_adapter.adapt(
        definition, confidence_level, user_prompt
    )
```

#### 7. `server/router/infrastructure/config.py`
```python
enable_workflow_adaptation: bool = True
adaptation_semantic_threshold: float = 0.6
```

### Implementation order
1. ✅ `base.py` - add `optional` and `tags` fields to WorkflowStep
2. ✅ `workflow_loader.py` - parse new fields
3. ✅ `picnic_table.yaml` - mark 16 bench steps as optional
4. ✅ `semantic_workflow_matcher.py` - use find_best_match_with_confidence
5. ✅ `workflow_adapter.py` - new engine
6. ✅ `config.py` - new config options
7. ✅ `router.py` - adapter integration
8. ✅ Tests
9. ✅ Documentation
10. ✅ Rebuild Docker image

### Expected result
```
"create a picnic table" → HIGH (0.92) → 49 steps (full workflow)
"simple table with 4 legs" → LOW (0.72) → ~33 steps (without benches)
"table with benches" → MEDIUM (0.78) → ~40 steps (core + bench)
```

---

## Implementation

### New files
- `server/router/application/engines/workflow_adapter.py` (~230 lines)
- `tests/unit/router/application/test_workflow_adapter.py` (~450 lines, 20 tests)

### Modified files
- `server/router/application/workflows/base.py`
- `server/router/infrastructure/workflow_loader.py`
- `server/router/application/workflows/custom/picnic_table.yaml`
- `server/router/application/matcher/semantic_workflow_matcher.py`
- `server/router/infrastructure/config.py`
- `server/router/application/router.py`
- `server/router/application/engines/__init__.py`
- `tests/unit/router/application/matcher/test_semantic_workflow_matcher.py`

---

## Tests

### New unit tests

| File | Description |
|------|-------------|
| `tests/unit/router/application/test_workflow_adapter.py` | **NEW** - 20 tests for WorkflowAdapter |

**Implemented tests:**
```python
- test_high_confidence_returns_all_steps() ✅
- test_high_confidence_result_metadata() ✅
- test_low_confidence_skips_all_optional() ✅
- test_low_confidence_preserves_core_steps() ✅
- test_none_confidence_skips_all_optional() ✅
- test_medium_confidence_filters_by_tags() ✅
- test_medium_confidence_without_matching_tags() ✅
- test_medium_confidence_partial_tag_match() ✅
- test_simple_table_prompt_skips_benches() ✅
- test_table_with_benches_includes_bench_steps() ✅
- test_empty_optional_steps_returns_core_only() ✅
- test_all_optional_steps_workflow() ✅
- test_adaptation_result_to_dict() ✅
- test_adaptation_result_contains_skipped_info() ✅
- test_should_adapt_returns_false_for_high() ✅
- test_should_adapt_returns_true_for_low_with_optional() ✅
- test_should_adapt_returns_false_without_optional() ✅
- test_semantic_fallback_when_no_tags() ✅
- test_semantic_fallback_below_threshold() ✅
- test_get_info_returns_config() ✅
```

### Update existing tests

| File | Changes |
|------|---------|
| `tests/unit/router/application/matcher/test_semantic_workflow_matcher.py` | Updated tests for `find_best_match_with_confidence()` |

---

## Documentation

### Router Documentation

| File | Changes |
|------|---------|
| `_docs/_ROUTER/README.md` | Added "WorkflowAdapter" section to components list |
| `_docs/_ROUTER/IMPLEMENTATION/README.md` | Added `32-workflow-adapter.md` to the list |
| `_docs/_ROUTER/IMPLEMENTATION/32-workflow-adapter.md` | **NEW** - WorkflowAdapter documentation |

### Workflow Documentation

| File | Changes |
|------|---------|
| `_docs/_ROUTER/WORKFLOWS/README.md` | Added section about `optional` and `tags` in workflow definitions |
| `_docs/_ROUTER/WORKFLOWS/creating-workflows-tutorial.md` | Added section about optional steps and adaptation |

### Changelog

| File | Changes |
|------|---------|
| `_docs/_CHANGELOG/README.md` | Added entry for TASK-051 |
| `_docs/_CHANGELOG/97-2025-12-07-confidence-based-workflow-adaptation.md` | **NEW** - changelog entry |

---

## Checklist

- [x] 1. `base.py` - add `optional` and `tags` fields to WorkflowStep
- [x] 2. `workflow_loader.py` - parse new fields from YAML
- [x] 3. `picnic_table.yaml` - mark 16 bench steps as optional
- [x] 4. `semantic_workflow_matcher.py` - use `find_best_match_with_confidence()`
- [x] 5. `workflow_adapter.py` - new engine
- [x] 6. `config.py` - new configuration options
- [x] 7. `router.py` - integrate adapter
- [x] 8. Unit tests
- [x] 9. Documentation
- [x] 10. Rebuild Docker image

---

## See Also

- [Changelog #97](../_CHANGELOG/97-2025-12-07-confidence-based-workflow-adaptation.md)
- [WorkflowAdapter Implementation](../_ROUTER/IMPLEMENTATION/32-workflow-adapter.md)
